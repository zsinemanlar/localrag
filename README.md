# My Local RAG

Bu uygulama, kendi dokümanlarıma soru sorabildiğim, hiçbir şeyin bilgisayarımdan çıkmadığı küçük bir RAG uygulaması olup, "Microsoft AI Innovators" programı için "Foundry Local ile ilk local RAG uygulaması" konusu için geliştirdiğim projedir.

İşleyiş: `docs/` klasörüne `.txt` veya `.md` dosyaları atıyorum, uygulama onları okuyup parçalara bölüyor, soru sorduğumda en alakalı parçaları bulup local bir dil modeline veriyor ve model o parçalara bakarak cevap yazıyor. Cevabın altında hangi dosyanın hangi bölümünden geldiği de görünüyor, böylece modele körü körüne güvenmek zorunda kalmıyorum.
Bağımlılıklar: `foundry-local-sdk` , `numpy`.

## Nasıl çalışıyor

İki aşama var. İlk aşama:

**Indexleme**:

1. `loader.py` klasördeki `.txt` ve `.md` dosyalarını okuyor.
2. `chunker.py` metni paragraf sınırlarına dokunmadan yaklaşık 130 kelimelik parçalara bölüyor. Ardışık parçalar arasında 25 kelimelik bir örtüşme (overlap) bırakıyor, böylece bir bilgi iki parçanın arasında kalıp kaybolmuyor. Markdown başlıklarını ayrı parça yapmıyorum, parçanın hangi bölümden geldiği bilgisi olarak saklıyorum.
3. Her parça embedding modelinden geçip 1024 boyutlu bir vektöre dönüşüyor.
4. Vektörler `data/vectors.npy`, parçaların metni `data/chunks.json` olarak diske yazılıyor. Docs'un içeriğinin bir özetini de saklıyorum; bir dosya değişirse ya da eklenirse uygulama bunu fark edip indexi kendisi yeniliyor.

**Soru sorma**:
1. Soru aynı embedding modeliyle vektöre çevriliyor.
2. Tüm parça vektörleriyle cosine similarity hesaplanıyor, en yüksek 4 parça alınıyor.
3. Benzerliği 0,45'in altında kalan parçaları atıyorum. Hiçbiri kalmazsa chat modelini hiç çağırmadan "dokümanlarda bulamadım" diyorum. Bu koleksiyonda ölçtüğüm değerler şöyleydi: alakalı sorular 0,50-0,65, alakasızlar 0,30-0,41. Eşik ise bu dokümanlara göre seçilmiş bir sayı, yani başka bir koleksiyonda yeniden bakmak gerektiğini gösteriyor.
4. Kalan parçalar numaralanıp prompt'a konuyor, model "yalnızca bu kaynaklara dayanarak cevapla ve [1] gibi numara ver" talimatıyla cevap yazıyor. Cevap token token akıyor.
5. Model atıf yapsa da yapmasa bulunan parçaların hepsini dosya adı, bölüm başlığı ve benzerlik skoruyla ayrıca listeliyorum.


## Foundry Local

Foundry Local, yapay zeka modellerini bulut yerine kendi cihazında çalıştıran bir Microsoft çalışma zamanıdır. Kullanırken benim için önemli olanlar:

- **Alias.** Kodda sadece `qwen3-8b` yazıyorum. Katalog bu model için birden fazla variant tutuyor (`cuda-gpu`, `generic-gpu`, `generic-cpu` gibi) ve SDK cihazdaki kayıtlı execution provider'lara bakıp uygun olanı seçiyor. Bu bilgisayarda (RTX 4070) CUDA variant'ı seçiliyor. GPU'suz bir makinede aynı kod CPU variant'ıyla çalışır, sadece yavaş olur.
- **Ayrıca Foundry Local kurmak gerekmiyor.** SDK'nın 2.x sürümü çalışma zamanını paketin içinde getiriyor, `pip install` yeterli.
- **Model akışı:** `catalog.get_model(alias)`, sonra `download(progress_callback)`, sonra `load()`. İndirilen model cache'te kalıyor ve sonraki açılışlarda tekrar inmiyor. İndirme sırasında terminalde ilerleme çubuğu çıkıyor.

## Hangi modeli neden seçtim:

**Embedding: `qwen3-embedding-0.6b`.** Çok dilli ve küçük (~0,5 GB), Türkçe dokümanlarda ilgili parçaları iyi ayırıyor. Sorguyu `Instruct: ... Query: ...` önekiyle embed ediyorum, ayrıca dokümanlar öneksiz gidiyor.
**Chat: `qwen3-8b`.** Burada çok zaman harcadım çünkü dokümanlar ve sorular Türkçe ve küçük modeller bunda ciddi şekilde zorlanıyor. Aynı prompt ve aynı sorularla şunları denedim:
- `qwen2.5-1.5b`: Türkçesi yetersiz, cevaplar bağlamdan kopuk ve anlamsızdı.
- `phi-4-mini`: Çoğu doğruydu ama bir soruda bağlamı yanlış okudu.
- `ministral-3-3b`: Akıcıydı ama kaynakta olmayan ayrıntılar ekledi.
- `qwen3-4b`: Çoğunu doğru yaptı ve hızlıydı, ama "Verilerim buluta gidiyor mu?" sorusunda cevabı tersine çevirdi.
- `qwen3-8b`: Denediğim tüm sorularda doğruydu, alakasız soruyu da doğru reddetti.


## Kurulum
Gereksinimler: Python 3.11 veya üstü (SDK bunu istiyor). Ben Python 3.13 ile çalıştım. Windows, Linux ve macOS (ARM64) destekleniyor; ben yalnızca Windows'ta denedim.

```bash
git clone https://github.com/zsinemanlar/localrag.git
cd localrag
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

**Model ve çalışma zamanı dosyalarının yeri.** Varsayılan olarak `D:\localrag` altına iniyor. Senin makinende D: yoksa ya da başka bir yer istiyorsan ortam değişkeni ver:

```bash
set LOCALRAG_HOME=C:\Users\sen\localrag-data      # Linux/macOS: export LOCALRAG_HOME=~/localrag-data
```

(`localrag/config.py` içindeki varsayılanı değiştirmek de olur.)

İlk çalıştırmada modeller iniyor: embedding ~0,5 GB, `qwen3-8b` ~5,6 GB. Terminalde ilerleme çubuğunu görüyorsun. Sonrasında cache'ten yükleniyor. Başka chat modeli denemek için:

```bash
set LOCALRAG_CHAT=qwen3-4b
```

## Kullanım

```bash
python app.py                    # terminalde soru-cevap döngüsü
python app.py ask "soru"         # tek soru sor ve çık
python app.py ingest --force     # indexi sıfırdan üret
python app.py web                # tarayıcı arayüzü: http://127.0.0.1:8080
```

Kendi dokümanlarını `docs/` klasörüne `.txt` ya da `.md` olarak koyup uygulamayı yeniden başlatman yeterli, index kendini yeniliyor. Klasörde hazır 5 örnek doküman var (Foundry Local, model yaşam döngüsü, donanım, gizlilik, RAG hakkında).

Arayüz standart kütüphanedeki `http.server` ile yazılmış tek bir HTML sayfası, ek bir web framework'ü yok. Sadece `127.0.0.1`'e bağlanıyor, dışarıdan erişilemez. Cevaptaki `[1]` gibi numaralara tıklayınca ilgili kaynak parçası açılıyor.

## Dosyalar

```
app.py               komut satırı (chat, ask, ingest, web)
web.py, web/         tarayıcı arayüzü
localrag/
  runtime.py         Foundry Local'ı başlatma, modeli indirme/yükleme
  loader.py          docs/ okuma
  chunker.py         parçalama
  store.py           numpy vektör deposu
  pipeline.py        ingest, arama, prompt, streaming, atıf
  config.py          model adları, eşikler, yollar
docs/                örnek dokümanlar
tests/               birim testleri
DEMO.md              video için notlar
```

## Testler

Model yüklemeden çalışan parçalar için (chunker, vektör deposu, dosya okuyucu, `<think>` ayıklama) 8 test var:

```bash
python -m unittest discover -s tests -t .
```
