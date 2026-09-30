# Demo notları (2 dakikalık video)

Konu: **Building Your First Local RAG Application with Foundry Local**. Video iki dakika, bu yüzden tek bir fikir anlatılıyor: *kendi dokümanların üzerinde, internet olmadan çalışan bir asistan ve cevabın nereden geldiği görünüyor.*

## Kayıttan önce (5 dakika)

1. **Isıt.** `python app.py web` komutunu kayıttan önce başlat ve bir soru sor. Model yükleme ve ilk çağrı 10-20 sn sürer; bunu videoya sokma.
2. **Temiz index.** İlk çalıştırmada progress çubuğunu göstermek istiyorsan `LOCALRAG_HOME`'u geçici bir klasöre yönlendirip embedding indirmesini kaydet (0,5 GB, kısa sürer). Chat modelinin 5,6 GB'lık indirmesini videoda bekleme; hazır cache ile başla.
3. **Ekran.** Terminal yazı boyutunu büyüt (en az 18 pt), tarayıcıyı %125 yakınlaştır, bildirimleri kapat. Sol yarıda editör/terminal, sağ yarıda tarayıcı düzeni iyi çalışır.
4. **Offline kanıtı.** Wi-Fi simgesini gösterip **uçak modunu aç** ve ondan sonra soru sor. Bu, videonun en güçlü anı. Uygulama açılırken SDK'nın birkaç ağ kontrolü yaptığını gördüm (cevap üretirken yapmıyor); ağ kapalıyken de açıldığını proxy ile simüle ederek denedim ama gerçek uçak modunda denemedim. Bu yüzden kayıttan önce bir kez gerçek uçak modunda baştan açıp dene; sunucuyu uçak modundan **önce** açmak en güvenlisi.

## Akış

| Süre | Ekranda | Söylenecek (özet) |
|---|---|---|
| 0:00-0:15 | `README.md`, "Nasıl çalışıyor" bölümü | "Bulut yok, API anahtarı yok. Foundry Local modelleri ONNX Runtime ile cihazda çalıştırıyor. Ben bunun üstüne küçük bir RAG kurdum, hiçbir framework kullanmadan." |
| 0:15-0:40 | `localrag/pipeline.py`, sırayla `ingest` → `retrieve` → `answer` | "Dokümanlar chunk'lara bölünüyor, her chunk qwen3-embedding ile vektöre çevriliyor. Vektör deposu düz bir numpy matrisi: normalize ettiğim için cosine similarity tek bir matris çarpımı. Bu ölçekte veritabanına gerek yok." |
| 0:40-0:55 | `localrag/runtime.py` içinde `catalog.get_model(alias)` | "Kodda sadece `qwen3-8b` yazıyor. SDK cihazı tanıyıp doğru variant'ı seçiyor: bu makinede CUDA. Aynı kod GPU'suz makinede CPU'da çalışır." |
| 0:55-1:05 | Terminalde `python app.py ingest --force` | "Beş doküman, yirmi chunk. Embedding'ler `data/` altına yazıldı, sonraki açılışta tekrar üretilmiyor." |
| 1:05-1:45 | Tarayıcı arayüzü, **uçak modu açık** | Soru 1: *Cihazda GPU yoksa ne olur?* Cevabın altındaki `[1]` çipine tıkla, kaynağın açılmasını göster. Soru 2: *Verilerim buluta gidiyor mu?* Soru 3: *İstanbul'da hava nasıl?* → "Dokümanlarda bulamadım." "Benzerlik eşiğinin altında kalınca model hiç çağrılmıyor, uydurmuyor." |
| 1:45-2:00 | Üst çubuk (qwen3-8b · CUDA · ağ isteği yok) ve README'deki "Hangi modeli neden seçtim" bölümü | "Küçük modellerle denedim: 1,5B Türkçede anlamsız cevap verdi, 4B bir olumsuzlu soruyu tersine çevirdi, 8B tutarlıydı. Model tek bir ortam değişkeniyle değişiyor. Kod GitHub'da." |

## Soru listesi (önceden denendi, bu dokümanlarla doğru cevap veriyor)

- Foundry Local modelleri hangi runtime üzerinde çalıştırır?
- Cihazda GPU yoksa ne olur?
- Model indirildikten sonra internet gerekir mi?
- Verilerim buluta gidiyor mu?
- Retrieval aşamasında hangi benzerlik ölçüsü kullanılır?
- Alakasız soru (reddetme gösterisi): İstanbul'da hava nasıl?

Aynı soru iki kez sorulduğunda cümleler birebir aynı olmayabilir (temperature 0,2). Kayıttan önce her soruyu bir kez dene; beğenmediğin bir cevap çıkarsa yeniden sor.

## Söylenmesi dürüst olan sınırlar

- Cevap kalitesi model boyutuna bağlı; bu yüzden kaynaklar hep gösteriliyor.
- SDK'nın `get_chat_client` API'si 2026 sonunda kalkıyor; yeni `ChatSession` API'sine geçiş küçük bir iş (README, "Eksikler ve bilmem gerekenler").
- Bu makinede CUDA ve TensorRT-RTX EP'lerini aynı process'te karıştırmak çöküyordu; embedding ve chat aynı EP'ye sabitlendi. İstersen bunu videoda "gerçek dünyada karşılaştığım bir sorun" olarak anlatabilirsin, ama süreye sığmıyorsa README'de duruyor.

## Repo (private) için

`.gitignore`, model dosyalarını ve `data/` index'ini dışarıda tutuyor; repoya yalnızca kod, `docs/` ve README girer.
