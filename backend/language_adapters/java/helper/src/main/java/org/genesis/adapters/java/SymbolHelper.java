package org.genesis.adapters.java;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.Problem;
import com.github.javaparser.Range;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.AnnotationDeclaration;
import com.github.javaparser.ast.body.BodyDeclaration;
import com.github.javaparser.ast.body.CallableDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.RecordDeclaration;
import com.github.javaparser.ast.body.TypeDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.nodeTypes.NodeWithModifiers;
import com.github.javaparser.ast.stmt.ExplicitConstructorInvocationStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.resolution.MethodAmbiguityException;
import com.github.javaparser.resolution.UnsolvedSymbolException;
import com.github.javaparser.resolution.declarations.ResolvedMethodLikeDeclaration;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JavaParserTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;

/**
 * Reads a source root (argument 1) and repository-relative .java paths (stdin, one per line)
 * and writes declarations and call references as JSON to stdout.
 *
 * <p>Positions are JavaParser-native: 1-based lines, 1-based UTF-16 columns with tab size 1,
 * and an inclusive end. The Python adapter converts them to CIR scalar columns with an
 * exclusive end using the original source bytes. Analysed source is parsed only; it is never
 * compiled, class-loaded or executed. Only JRE classes are resolved by reflection.
 */
public final class SymbolHelper {
    private static final int MAX_REASON = 1500;

    private SymbolHelper() {
    }

    public static void main(String[] args) throws IOException {
        // JavaParser lower-cases keywords with the default locale; a Turkish locale turns
        // "INT" into "ınt" and breaks every primitive signature. Analysis is locale-neutral.
        Locale.setDefault(Locale.ROOT);
        if (args.length != 1) {
            System.err.println("usage: SymbolHelper <source-root> < relative-paths");
            System.exit(2);
        }
        Path root = Path.of(args[0]).toRealPath();
        List<String> relativePaths = new ArrayList<>();
        try (BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                if (!line.isEmpty()) {
                    relativePaths.add(line);
                }
            }
        }
        Json out = new Json();
        new SymbolHelper().run(root, relativePaths, out);
        PrintWriter writer = new PrintWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8));
        writer.print(out);
        writer.flush();
    }

    private static ParserConfiguration baseConfiguration() {
        return new ParserConfiguration()
                .setLanguageLevel(ParserConfiguration.LanguageLevel.JAVA_21)
                .setCharacterEncoding(StandardCharsets.UTF_8)
                .setTabSize(1)
                .setPreprocessUnicodeEscapes(false)
                .setStoreTokens(true);
    }

    private void run(Path root, List<String> relativePaths, Json out) throws IOException {
        Properties properties = new Properties();
        try (InputStream stream = SymbolHelper.class.getResourceAsStream("/helper.properties")) {
            if (stream != null) {
                properties.load(stream);
            }
        }
        // Pass 1: syntax only, to find package-based source roots for the type solver.
        JavaParser syntaxOnly = new JavaParser(baseConfiguration());
        Set<Path> sourceRoots = new LinkedHashSet<>();
        for (String relative : relativePaths) {
            Path file = resolveInside(root, relative);
            ParseResult<CompilationUnit> result = syntaxOnly.parse(file);
            Path directory = file.getParent();
            Optional<String> pkg = result.getResult().flatMap(CompilationUnit::getPackageDeclaration)
                    .map(declaration -> declaration.getNameAsString());
            Path sourceRoot = directory;
            if (pkg.isPresent()) {
                Path expected = Path.of("", pkg.get().split("\\."));
                if (directory.endsWith(expected)) {
                    sourceRoot = directory;
                    for (int i = 0; i < expected.getNameCount(); i++) {
                        sourceRoot = sourceRoot.getParent();
                    }
                }
            }
            if (sourceRoot != null && sourceRoot.startsWith(root)) {
                sourceRoots.add(sourceRoot);
            }
        }
        CombinedTypeSolver typeSolver = new CombinedTypeSolver();
        typeSolver.add(new ReflectionTypeSolver(true));
        for (Path sourceRoot : sourceRoots) {
            typeSolver.add(new JavaParserTypeSolver(sourceRoot, baseConfiguration()));
        }
        ParserConfiguration resolving = baseConfiguration().setSymbolResolver(new JavaSymbolSolver(typeSolver));
        JavaParser parser = new JavaParser(resolving);

        out.beginObject();
        out.name("tool").beginObject()
                .field("helper", "java-symbol-helper")
                .field("helper_version", properties.getProperty("helper.version"))
                .field("parser", "javaparser-symbol-solver-core")
                .field("parser_version", properties.getProperty("javaparser.version"))
                .field("java_version", System.getProperty("java.version"))
                .field("java_vendor", System.getProperty("java.vendor"))
                .endObject();
        out.name("configuration").beginObject()
                .field("language_level", "JAVA_21")
                .field("tab_size", 1L)
                .field("column_unit", "UTF16_CODE_UNIT")
                .field("end", "INCLUSIVE")
                .field("preprocess_unicode_escapes", false)
                .field("type_solvers", "ReflectionTypeSolver(jreOnly)+JavaParserTypeSolver(package roots)")
                .endObject();
        out.name("source_roots").beginArray();
        for (Path sourceRoot : sourceRoots) {
            out.value(relativize(root, sourceRoot));
        }
        out.endArray();
        out.name("files").beginArray();
        for (String relative : relativePaths) {
            analyse(parser, root, relative, out);
        }
        out.endArray();
        out.endObject();
    }

    private static Path resolveInside(Path root, String relative) throws IOException {
        Path file = root.resolve(relative).normalize();
        if (!file.startsWith(root) || !Files.isRegularFile(file, java.nio.file.LinkOption.NOFOLLOW_LINKS)) {
            throw new IOException("path is outside the source root or not a regular file");
        }
        return file;
    }

    private static String relativize(Path root, Path path) {
        String value = root.relativize(path).toString().replace('\\', '/');
        return value.isEmpty() ? "." : value;
    }

    private void analyse(JavaParser parser, Path root, String relative, Json out) {
        out.beginObject().field("path", relative);
        ParseResult<CompilationUnit> result;
        try {
            result = parser.parse(resolveInside(root, relative));
        } catch (IOException | RuntimeException error) {
            out.field("status", "IO_ERROR").field("reason", reason(error))
                    .name("problems").beginArray().endArray()
                    .name("declarations").beginArray().endArray()
                    .name("references").beginArray().endArray().endObject();
            return;
        }
        out.field("status", result.isSuccessful() ? "PARSED" : "PARSE_ERROR").field("reason", (String) null);
        out.name("problems").beginArray();
        for (Problem problem : result.getProblems()) {
            out.beginObject().field("message", truncate(problem.getVerboseMessage()));
            Optional<Range> range = problem.getLocation().flatMap(tokens -> tokens.getBegin().getRange());
            out.name("range");
            range(range, out);
            out.endObject();
        }
        out.endArray();
        if (!result.isSuccessful() || result.getResult().isEmpty()) {
            out.name("declarations").beginArray().endArray().name("references").beginArray().endArray().endObject();
            return;
        }
        CompilationUnit unit = result.getResult().get();
        out.name("declarations").beginArray();
        for (TypeDeclaration<?> type : unit.findAll(TypeDeclaration.class)) {
            String name = type.getFullyQualifiedName().orElse(null);
            out.beginObject().field("kind", typeKind(type)).field("name", type.getNameAsString())
                    .field("signature", name).field("resolved", name != null)
                    .field("reason", name == null ? "local or anonymous type has no fully qualified name" : null)
                    .field("public_api", publicApi(type));
            out.name("range");
            range(type.getRange(), out);
            out.name("name_range");
            range(type.getName().getRange(), out);
            out.endObject();
        }
        for (CallableDeclaration<?> callable : unit.findAll(CallableDeclaration.class)) {
            String kind = callable instanceof ConstructorDeclaration ? "CONSTRUCTOR" : "METHOD";
            String signature;
            String failure = null;
            try {
                signature = resolveCallable(callable).getQualifiedSignature();
            } catch (RuntimeException error) {
                signature = callable.getDeclarationAsString(false, false, false);
                failure = classify(error) + ": " + referenceReason(error);
            }
            out.beginObject().field("kind", kind).field("name", callable.getNameAsString())
                    .field("signature", signature).field("resolved", failure == null)
                    .field("reason", failure).field("public_api", publicApi(callable));
            out.name("range");
            range(callable.getRange(), out);
            out.name("name_range");
            range(callable.getName().getRange(), out);
            out.endObject();
        }
        for (FieldDeclaration field : unit.findAll(FieldDeclaration.class)) {
            Optional<String> owner = field.findAncestor(TypeDeclaration.class)
                    .flatMap(TypeDeclaration::getFullyQualifiedName);
            for (VariableDeclarator variable : field.getVariables()) {
                String signature = owner.map(type -> type + "." + variable.getNameAsString()).orElse(null);
                out.beginObject().field("kind", "FIELD").field("name", variable.getNameAsString())
                        .field("signature", signature).field("resolved", signature != null)
                        .field("reason", signature == null ? "field owner has no fully qualified name" : null)
                        .field("public_api", publicApi(field));
                out.name("range");
                range(variable.getRange(), out);
                out.name("name_range");
                range(variable.getName().getRange(), out);
                out.endObject();
            }
        }
        out.endArray();

        out.name("references").beginArray();
        for (Node node : unit.findAll(Node.class)) {
            if (node instanceof MethodCallExpr call) {
                reference(out, "METHOD_CALL", call.getNameAsString(), call, call.getName().getRange(),
                        call.getArguments().size(), () -> call.resolve());
            } else if (node instanceof ObjectCreationExpr creation) {
                reference(out, "CONSTRUCTOR_CALL", creation.getType().getNameAsString(), creation,
                        creation.getType().getRange(), creation.getArguments().size(),
                        () -> creation.resolve());
            } else if (node instanceof ExplicitConstructorInvocationStmt invocation) {
                reference(out, "EXPLICIT_CONSTRUCTOR_CALL", invocation.isThis() ? "this" : "super", invocation,
                        invocation.getRange(), invocation.getArguments().size(), () -> invocation.resolve());
            }
        }
        out.endArray();
        out.endObject();
    }

    private interface Resolver {
        ResolvedMethodLikeDeclaration resolve();
    }

    private void reference(Json out, String kind, String name, Node node, Optional<Range> nameRange,
                           int argumentCount, Resolver resolver) {
        out.beginObject().field("kind", kind).field("name", name).field("from", enclosing(node))
                .field("argument_count", argumentCount);
        out.name("range");
        range(node.getRange(), out);
        out.name("name_range");
        range(nameRange, out);
        try {
            ResolvedMethodLikeDeclaration target = resolver.resolve();
            String origin = target.toAst().isPresent() ? "SOURCE"
                    : target.declaringType().toAst().isPresent() ? "IMPLICIT" : "EXTERNAL";
            out.field("status", "RESOLVED").field("target", target.getQualifiedSignature())
                    .field("target_origin", origin)
                    .field("declaring_type", target.declaringType().getQualifiedName())
                    .field("reason", (String) null);
        } catch (RuntimeException error) {
            out.field("status", classify(error)).field("target", (String) null)
                    .field("target_origin", (String) null).field("declaring_type", (String) null)
                    .field("reason", referenceReason(error));
        } catch (StackOverflowError error) {
            out.field("status", "ERROR").field("target", (String) null)
                    .field("target_origin", (String) null).field("declaring_type", (String) null)
                    .field("reason", "symbol solver recursion limit exceeded");
        }
        out.endObject();
    }

    private static String enclosing(Node node) {
        Optional<CallableDeclaration> callable = node.findAncestor(CallableDeclaration.class);
        if (callable.isPresent()) {
            try {
                return resolveCallable(callable.get()).getQualifiedSignature();
            } catch (RuntimeException error) {
                return callable.get().getDeclarationAsString(false, false, false);
            }
        }
        Optional<VariableDeclarator> variable = node.findAncestor(VariableDeclarator.class);
        Optional<FieldDeclaration> field = node.findAncestor(FieldDeclaration.class);
        Optional<String> owner = node.findAncestor(TypeDeclaration.class)
                .flatMap(TypeDeclaration::getFullyQualifiedName);
        if (field.isPresent() && variable.isPresent() && owner.isPresent()) {
            return owner.get() + "." + variable.get().getNameAsString();
        }
        return owner.orElse(null);
    }

    private static ResolvedMethodLikeDeclaration resolveCallable(CallableDeclaration<?> callable) {
        if (callable instanceof MethodDeclaration method) {
            return method.resolve();
        }
        if (callable instanceof ConstructorDeclaration constructor) {
            return constructor.resolve();
        }
        throw new UnsupportedOperationException("unsupported callable declaration");
    }

    private static String classify(Throwable error) {
        if (error instanceof MethodAmbiguityException) {
            return "AMBIGUOUS";
        }
        if (error instanceof UnsolvedSymbolException) {
            return "MISSING_DEPENDENCY";
        }
        if (error instanceof UnsupportedOperationException) {
            return "UNSUPPORTED";
        }
        return "ERROR";
    }

    /**
     * Resolution failures name the failure class and, for an unsolved symbol, only that
     * identifier. Solver messages embed raw source fragments, which CIR reasons must not carry.
     */
    private static String referenceReason(Throwable error) {
        if (error instanceof MethodAmbiguityException) {
            return "more than one applicable declaration; no most specific overload";
        }
        if (error instanceof UnsolvedSymbolException unsolved && unsolved.getName() != null
                && unsolved.getName().matches("[\\p{L}\\p{N}_$.<>\\[\\], ]{1,200}")) {
            return "unsolved symbol: " + unsolved.getName();
        }
        return "symbol solver failure: " + error.getClass().getSimpleName();
    }

    private static String reason(Throwable error) {
        String message = error.getMessage();
        return truncate(error.getClass().getSimpleName() + (message == null ? "" : ": " + message));
    }

    private static String truncate(String value) {
        if (value == null) {
            return null;
        }
        String single = value.replaceAll("\\s+", " ").trim();
        return single.length() <= MAX_REASON ? single : single.substring(0, MAX_REASON) + "...";
    }

    private static String typeKind(TypeDeclaration<?> type) {
        if (type instanceof RecordDeclaration) {
            return "RECORD";
        }
        if (type instanceof EnumDeclaration) {
            return "ENUM";
        }
        if (type instanceof AnnotationDeclaration) {
            return "ANNOTATION";
        }
        if (type instanceof ClassOrInterfaceDeclaration declaration && declaration.isInterface()) {
            return "INTERFACE";
        }
        return "CLASS";
    }

    /** True only when the member and every enclosing type are effectively public. */
    private static boolean publicApi(Node node) {
        Node current = node;
        while (current != null) {
            if (current instanceof ObjectCreationExpr) {
                return false; // members of anonymous classes are not public API
            }
            if (current instanceof BodyDeclaration<?>) {
                boolean explicit = current instanceof NodeWithModifiers<?> modifiers
                        && modifiers.hasModifier(Modifier.Keyword.PUBLIC);
                boolean implicit = current.getParentNode()
                        .filter(parent -> parent instanceof ClassOrInterfaceDeclaration declaration
                                && declaration.isInterface()
                                || parent instanceof AnnotationDeclaration)
                        .isPresent()
                        && !(current instanceof NodeWithModifiers<?> modifiers
                        && modifiers.hasModifier(Modifier.Keyword.PRIVATE));
                if (!explicit && !implicit) {
                    return false;
                }
                if (current instanceof TypeDeclaration<?>
                        && current.getParentNode().filter(parent -> parent instanceof Statement).isPresent()) {
                    return false; // local class or record declared inside a method body
                }
            }
            current = current.getParentNode().orElse(null);
        }
        return true;
    }

    private static void range(Optional<Range> range, Json out) {
        if (range.isEmpty()) {
            out.nullValue();
            return;
        }
        Range value = range.get();
        out.beginArray().value(value.begin.line).value(value.begin.column)
                .value(value.end.line).value(value.end.column).endArray();
    }

    /** Minimal streaming JSON writer; avoids an additional runtime dependency. */
    static final class Json {
        private final StringBuilder text = new StringBuilder();
        private final List<Boolean> first = new ArrayList<>();
        private boolean afterName;

        private void separator() {
            if (afterName) {
                afterName = false;
                return;
            }
            if (!first.isEmpty()) {
                int last = first.size() - 1;
                if (!first.get(last)) {
                    text.append(',');
                }
                first.set(last, false);
            }
        }

        Json beginObject() {
            separator();
            text.append('{');
            first.add(true);
            return this;
        }

        Json endObject() {
            first.remove(first.size() - 1);
            text.append('}');
            return this;
        }

        Json beginArray() {
            separator();
            text.append('[');
            first.add(true);
            return this;
        }

        Json endArray() {
            first.remove(first.size() - 1);
            text.append(']');
            return this;
        }

        Json name(String name) {
            separator();
            string(name);
            text.append(':');
            afterName = true;
            return this;
        }

        Json field(String name, String value) {
            return name(name).value(value);
        }

        Json field(String name, long value) {
            return name(name).value(value);
        }

        Json field(String name, boolean value) {
            name(name);
            separator();
            text.append(value);
            return this;
        }

        Json value(String value) {
            if (value == null) {
                return nullValue();
            }
            separator();
            string(value);
            return this;
        }

        Json value(long value) {
            separator();
            text.append(value);
            return this;
        }

        Json nullValue() {
            separator();
            text.append("null");
            return this;
        }

        private void string(String value) {
            text.append('"');
            for (int i = 0; i < value.length(); i++) {
                char c = value.charAt(i);
                switch (c) {
                    case '"' -> text.append("\\\"");
                    case '\\' -> text.append("\\\\");
                    case '\n' -> text.append("\\n");
                    case '\r' -> text.append("\\r");
                    case '\t' -> text.append("\\t");
                    default -> {
                        if (c < 0x20 || Character.isSurrogate(c)) {
                            text.append(String.format("\\u%04x", (int) c));
                        } else {
                            text.append(c);
                        }
                    }
                }
            }
            text.append('"');
        }

        @Override
        public String toString() {
            return text.toString();
        }
    }
}
