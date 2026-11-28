import java.io.IOException;
import java.io.UncheckedIOException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import net.sourceforge.pmd.PMDVersion;
import net.sourceforge.pmd.cpd.CPDConfiguration;
import net.sourceforge.pmd.cpd.CPDReport;
import net.sourceforge.pmd.cpd.CpdAnalysis;
import net.sourceforge.pmd.lang.LanguageRegistry;
import net.sourceforge.pmd.lang.document.FileId;

class CpdXml {
    public static void main(String[] args) throws IOException {
        var config = new CPDConfiguration();
        config.setMinimumTileSize(Integer.parseInt(args[2]));
        config.setSourceEncoding(StandardCharsets.UTF_8);
        var java = LanguageRegistry.CPD.getLanguageById("java");
        config.setOnlyRecognizeLanguage(java);
        config.setForceLanguageVersion(java.getVersion("21"));

        var displayPaths = new HashMap<String, String>();
        var status = new AtomicInteger(1);
        Path root = Path.of("").toRealPath();
        try (var analysis = CpdAnalysis.create(config);
             var output = Files.newBufferedWriter(Path.of(args[1]), StandardCharsets.UTF_8)) {
            for (String name : Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8)) {
                Path relative = Path.of(name);
                Path file = root.resolve(relative);
                if (relative.isAbsolute() || name.contains(":") || name.contains("\\")
                        || !relative.normalize().equals(relative) || Files.isSymbolicLink(file)
                        || !file.toRealPath().startsWith(root) || !analysis.files().addFile(file)) {
                    throw new IOException("CPD input is outside the manifest file list");
                }
                displayPaths.put(file.toString(), name);
            }
            analysis.performAnalysis(report -> {
                try {
                    render(report, output, displayPaths);
                    status.set(!report.getProcessingErrors().isEmpty() ? 5
                            : report.getMatches().isEmpty() ? 0 : 4);
                } catch (XMLStreamException exception) {
                    throw new UncheckedIOException(new IOException("could not render CPD XML"));
                }
            });
        }
        System.exit(status.get());
    }

    // CPD 7.29.0's CLI XML always prints absolute paths. Render the real CPD
    // report at the tool boundary using the identities from the supplied file list.
    private static void render(CPDReport report, Writer output, Map<String, String> paths)
            throws XMLStreamException {
        XMLStreamWriter xml = XMLOutputFactory.newFactory().createXMLStreamWriter(output);
        try {
            xml.writeStartDocument("UTF-8", "1.0");
            xml.writeStartElement("pmd-cpd");
            xml.writeAttribute("pmdVersion", PMDVersion.VERSION);
            for (var file : report.getNumberOfTokensPerFile().entrySet()) {
                xml.writeEmptyElement("file");
                xml.writeAttribute("path", displayPath(file.getKey(), paths));
                xml.writeAttribute("totalNumberOfTokens", file.getValue().toString());
            }
            for (var match : report.getMatches()) {
                xml.writeStartElement("duplication");
                xml.writeAttribute("tokens", Integer.toString(match.getTokenCount()));
                xml.writeAttribute("lines", Integer.toString(match.getLineCount()));
                for (var mark : match) {
                    var location = mark.getLocation();
                    xml.writeEmptyElement("file");
                    xml.writeAttribute("path", displayPath(location.getFileId(), paths));
                    xml.writeAttribute("line", Integer.toString(location.getStartLine()));
                    xml.writeAttribute("column", Integer.toString(location.getStartColumn()));
                    xml.writeAttribute("endline", Integer.toString(location.getEndLine()));
                    xml.writeAttribute("endcolumn", Integer.toString(location.getEndColumn()));
                    xml.writeAttribute("begintoken", Integer.toString(mark.getBeginTokenIndex()));
                    xml.writeAttribute("endtoken", Integer.toString(mark.getEndTokenIndex()));
                }
                xml.writeEndElement();
            }
            for (var error : report.getProcessingErrors()) {
                xml.writeEmptyElement("error");
                xml.writeAttribute("path", displayPath(error.getFileId(), paths));
            }
            xml.writeEndElement();
            xml.writeEndDocument();
        } finally {
            xml.close();
        }
    }

    private static String displayPath(FileId file, Map<String, String> paths)
            throws XMLStreamException {
        String relative = paths.get(file.getAbsolutePath());
        if (relative == null) {
            throw new XMLStreamException("CPD returned a file outside the manifest file list");
        }
        return relative;
    }
}
