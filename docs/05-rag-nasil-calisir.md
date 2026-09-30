# RAG nasıl çalışır?

RAG, Retrieval-Augmented Generation'ın kısaltmasıdır. Dil modelinin cevabını, modelin eğitim verisine değil, sorgu anında bulunan dokümanlara dayandırma yöntemidir. Böylece model, eğitiminde hiç görmediği özel dokümanlar hakkında da cevap verebilir.

## Ingestion aşaması

Önce dokümanlar okunur ve chunk adı verilen küçük parçalara bölünür. Chunk'lar çok uzun olursa alakasız bilgi taşır, çok kısa olursa bağlamını kaybeder. Bu yüzden genelde birkaç yüz kelimelik, paragraf sınırlarına saygılı parçalar tercih edilir. Ardışık chunk'ların birkaç cümle ortak içermesine overlap denir; bir bilginin iki chunk arasında bölünüp kaybolmasını önler.

Her chunk bir embedding modeline verilir ve sabit uzunlukta bir vektöre dönüşür. Anlamca benzer metinlerin vektörleri birbirine yakın olur. Vektörler bir vector store'da saklanır.

## Retrieval aşaması

Kullanıcının sorusu da aynı embedding modeliyle vektöre çevrilir. Soru vektörü ile tüm chunk vektörleri arasındaki cosine similarity hesaplanır ve en yüksek skorlu top-k chunk seçilir. Küçük koleksiyonlarda bu hesap bir matris çarpımıdır ve milisaniyeler sürer.

## Generation aşaması

Seçilen chunk'lar prompt'a bağlam olarak eklenir ve chat modeline "sadece bu kaynaklara dayanarak cevapla" talimatı verilir. Model kaynakları numaralı kullanırsa cevaba citation eklenebilir. Hiçbir chunk yeterince benzer değilse modele gitmeden "bulunamadı" demek, uydurma cevap riskini azaltır.
