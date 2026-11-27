# Project Genesis — F04-JAVA teslim ve kabul raporu

| Alan | Kayıt |
|---|---|
| Görev | F04-JAVA / [#14](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/14): Language Router, Java sembol adaptörü ve yetenek manifesti (FR-008, FR-010, FR-011) |
| Geliştirici | Alperen Enes Yaman (`Yaman-A-E`), rotasyon indeksi 2 |
| Önkoşullar | F02-CONTRACT #11 ve F03-INPUT #13; ikisi de `completed` ve kabul kaydında mevcut |
| Uygulama PR'ı | [#67](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/67). Uygulama commit'i `cf34d198a1753e84629df34cf5711b5989178c89`, son HEAD `96009c01f9882b4a554ea44d1837c3e3f05179ac` (yalnızca `main` birleştirmesi) |
| Merge commit'i | `2c3d35a70b2c94e12fe172392a6098dc0ab520d5` |
| CI bağlantısı | Yönetişim PR'ı [#66](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/pull/66), merge `82f082b3969950de0d9d7c188184e9ee24a9b41e` |
| Teknik rapor | [docs/F04-JAVA.md @ 2c3d35a](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2c3d35a70b2c94e12fe172392a6098dc0ab520d5/docs/F04-JAVA.md) |
| Durum | `MERGED` · `HOSTED_VERIFIED` · bağımsız inceleme **yok** (aşağıya bakın) · kabul geliştiricinin açık talimatıyla kaydedildi |
| Sıradaki | F05-QUALITY / [#15](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/issues/15), İsmail Çevik (`ismail-cevik`), rotasyon indeksi 3 |

Önceki rapor (Genesis v3 Faz 1) değişmeden korunur: [report.md @ 2c3d35a](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/blob/2c3d35a70b2c94e12fe172392a6098dc0ab520d5/report.md).

## Teslim edilenler

| Bileşen | Konum | Davranış |
|---|---|---|
| Dil yönlendirici | `backend/language_adapters/router.py` | F03 manifestindeki her dosyaya açık bir durum verir: `ROUTED`, `UNSUPPORTED_LANGUAGE` veya `UNKNOWN_LANGUAGE`. Bileşen = (build kökü, dil). Kullanıcının dil tercihi yalnızca ipucudur ve tespit edilen dili değiştirmez. |
| Java yardımcısı | `backend/language_adapters/java/helper/` | Java 21/Maven ile `javaparser-symbol-solver-core` 3.28.2. JRE yansıma ile, proje tipleri paket köklerinden çözülür. Yüklenen kod derlenmez, yüklenmez, çalıştırılmaz. `Locale.ROOT` ile çalışır: Türkçe locale'de JavaParser `int` tipini `ınt` üretiyordu. |
| Java adaptörü | `backend/language_adapters/java/adapter.py` | Overload'a tam bağlı `Symbol`, `SourceLocation`, `DependencyEdge` (`CALL`) ve `Evidence` kayıtları. Belirsiz overload, eksik bağımlılık ve ayrıştırma hatası açık durum ve nedenle kalır; nedenlerde ham kaynak kod yoktur. |
| Koordinatlar | `backend/language_adapters/coordinates.py` | JavaParser UTF-16 (bitiş dahil) → CIR Unicode scalar (bitiş hariç) → Monaco UTF-16. CRLF, tab ve astral karakterler doğru işlenir. Standalone CR veya geçersiz UTF-8 için koordinat tahmin edilmez. |
| Yetenek manifesti | `backend/language_adapters/capabilities.py` | Dokuz bağımsız kayıt. `parse`, `symbol`, `dependency` yalnızca çalıştırma kanıtıyla `SUPPORTED`; güven değeri gözlenen çözümleme oranıdır. `quality`, `build`, `test`, `coverage`, `safe_patch`, `security` gerekçeli `NOT_IMPLEMENTED`. |
| Giriş noktası | `backend/language_adapters/analysis.py` | V0'ı `SourceSnapshots.workspace` üzerinden okur, her dosyanın SHA-256'sını manifestle yeniden doğrular, bundle'ı `validate_bundle` ile doğrular. |

## Kabul ölçütleri

| #14 ölçütü | Kanıt | Sonuç |
|---|---|---|
| Overload'lar doğru sembollere ve Monaco konumlarına eşlenir | Dosyalar arası, alan başlatıcısı ve `this(...)` çağrıları; CRLF, tab, emoji ve astral tanımlayıcı; `frontend/src/coordinates.ts` ile çapraz kontrol | PASS |
| Bilinmeyen ve karışık dilli dosyalar sessizce Java olarak ayrıştırılmaz | Yardımcıya yalnızca `.java` dosyaları gider; `Snippet.java.txt`, `.py`, `.ts` ve build dosyaları açık durumla raporlanır | PASS |
| Belirsiz referanslar belirsizliğini korur | `pick(null)` → `AMBIGUOUS` + iki aday imza; `Lib.call()` → `MISSING_DEPENDENCY`; çağrı konumu korunur | PASS |
| Yetenekler analizi `safe_patch`ten ayırır | `require_capability` parse/symbol/dependency için geçer; safe_patch/build/test için `UNAVAILABLE_CAPABILITY` verir | PASS |

## Doğrulama

| Kontrol | Ortam | Sonuç |
|---|---|---|
| `tests/language_adapters` (27 test) | Hosted Linux, PR HEAD [run 45916669843](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/actions/runs/45916669843) ve merge [run 45916724832](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/actions/runs/45916724832) | PASS · 27 passed, 0 skipped |
| `backend-checks`, `governance-tests`, `documentation-checks`, `security-checks`, `pilot-checks`, `application-stack-checks`, `task-dependency-audit` | Hosted, PR HEAD ve merge commit'i | PASS ([PR kontrolleri](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/commit/96009c01f9882b4a554ea44d1837c3e3f05179ac/checks) · [merge kontrolleri](https://github.com/refactoring-ai-code/refactoring-ai-generated-code/commit/2c3d35a70b2c94e12fe172392a6098dc0ab520d5/checks)) |
| Adaptör testleri, ruff, sözleşme kontrolleri (55 test, export güncel), pilot `verify_integrity.py` ×2 ve `reproduce.py` (10/10 JUnit) | Yerel Windows 11, Temurin 21.0.13.1, Maven 3.9.11 | PASS |
| `pytest backend/tests` 38/39, `governance-tests` 81/83 | Yerel Windows | Ters eğik çizgili yol testi ve iki symlink testi, değiştirilmemiş `main` (`eb0a6d3`) üzerinde de Windows'ta başarısız. F04 ile ilgisiz; hosted Linux'ta geçiyor. |

V0, Java pilotu ve sabit test dosyalarının SHA-256 değerleri değişmedi. `experiments/`, `tests/fixtures/` ve korunan dosyalara dokunulmadı. Merge edilen F04 içeriği, incelemeye sunulan `cf34d19` ile birebir aynı.

## Sapmalar ve açık noktalar

- **Bağımsız inceleme yok.** #14 İsmail'i bağımsız incelemeci olarak belirtiyor; PR #67 GitHub incelemesi olmadan merge edildi. `main` koruması onay istemediği için GitHub buna izin verdi. Kabul, aktif geliştiricinin açık talimatıyla kaydedildi. `96009c0` için merge sonrası bir inceleme önerilir. Bu kayıt bağımsız inceleme iddia etmez.
- **Sınırlamalar.** Yalnızca `CALL` kenarları üretilir. Metot referansları ve yerel değişkenler modellenmez. Üçüncü taraf kütüphaneler `MISSING_DEPENDENCY` olarak kalır. Ayrıntılar teknik raporda.
- Kalite ölçümü (F05), sandbox build/test/coverage (F06), güvenlik taraması (F07A) ve patch (F10/F11) kendi görevlerine aittir.

## Devir

Rotasyon bir kez 2 → 3 ilerledi; anahtar `F04-JAVA:96009c01f9882b4a554ea44d1837c3e3f05179ac`. Plan sırasındaki ilk hazır görev F05-QUALITY / #15. Tek önkoşulu #14; kapsamı, kabul ölçütleri ve izinli yolları değiştirilmedi. Sorumlusu İsmail Çevik (`ismail-cevik`). Kabulden sonraki koşullu sorumlu Taha Uğur Toyran (`tahaugurtoyran`).

## Ek: 2026-11-27 dokümantasyon bakımı (F01-GOV / #1)

F04-JAVA kabulünden sonra güncellenmeyen belgeler, gerçek duruma göre düzeltildi. Ürün kodu, görev ataması, kabul kaydı, rotasyon ve dondurulmuş pilot dosyaları değişmedi. Aktif görev F05-QUALITY / #15, İsmail Çevik; sıradaki Taha Uğur Toyran. Bakım, proje içi rotasyon turu tüketmez.

| Dosya | Düzeltme |
|---|---|
| `README.md` | 9/34 kabul, aktif F05-QUALITY; repo erişimi (beş hesap Admin, 2026-11-27); SRS v0.4.1; ADR 0007 ile kalkan tek onaycı kuralı |
| `docs/PROJECT_STATUS.md` | Üst not güncellendi; 2026-11-27 bakım bölümü eklendi |
| `docs/DEVELOPMENT_ROADMAP.md` | Canlı durum notu, Status satırı, F04/F05 satırları, mevcut yetkili geliştirme; tek onaycı ve v2.1 ifadeleri; yerel model adı |
| `docs/F04-JAVA.md` | "CI gap" paragrafı → PR #66 sonrası hosted CI durumu |
| `docs/ARCHITECTURE.md` | Hatalı "replacing Qwen3-Coder" parantezi kaldırıldı; diyagramda yerel Qwen3-Coder incelemesi zorunlu |
| `docs/SRS.md`, `docs/SRS_EN.md` | Paralel refactoring işi en fazla altı; taslak / onay bekliyor ifadeleri düzeltildi; "7B" → Qwen3-Coder 30B-A3B; PR #38 merge edildi (`5754ed6`). FR/NFR kimlikleri ve öncelikleri değişmedi |
| `docs/contracts/README.md`, `CONSUMERS.md` | F02 kabulü ve Java runtime adaptörü |
| `docs/DECISIONS/0003`, `0005` | Başlığa sonraki durum / amendment notu; karar metni değişmedi |
| `docs/visualizations/` | `maxParallel: 6`; SRS v0.4.1 |
| `infrastructure/README.md` | Yayındaki application-stack CI; Java araç zinciri notu |
| `experiments/` README'leri | PR #45 merge edildi (`fdd5732`), F00-V0 kabul edildi; manifestler değişmedi |
| `.github/workflows/governance-ci.yml`, `issue-graph-sync.yml`, `SECURITY.md` | Emekli bootstrap dallarına tetik kaldırıldı |
| `.agents/skills/verification/SKILL.md` | Pilot manifest uyuşmazlığının PR #48 ile giderildiği |

Doğrulama sonuçları ve merge kanıtı bu değişikliğin PR'ında kayıtlıdır.
