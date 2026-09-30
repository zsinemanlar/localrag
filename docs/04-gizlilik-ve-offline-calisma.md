# Gizlilik ve offline çalışma

Bir RAG uygulamasında iki tür veri modele gider: kullanıcının sorusu ve dokümanlardan çekilen parçalar. Bulut tabanlı bir servis kullanıldığında ikisi de şirket dışına çıkar. Foundry Local ile hem embedding hem de cevap üretme cihazda yapıldığı için hiçbir metin ağa gönderilmez.

## Neyi garanti eder?

Inference cihazda gerçekleşir. Sorgu metni, doküman içeriği ve üretilen cevap bilgisayardan çıkmaz. API anahtarı olmadığı için anahtar sızıntısı riski de yoktur. Model dosyaları indirildikten sonra ağ bağlantısı kesilse bile uygulama çalışmaya devam eder.

## Neyi garanti etmez?

Yerel çalışma, uygulamanın güvenli olduğu anlamına gelmez. Index dosyaları diskte düz metin olarak durur; diske erişimi olan biri dokümanların parçalarını okuyabilir. Ayrıca küçük modeller hata yapabilir. Bu yüzden cevaplarda kaynak gösterilmesi önemlidir: kullanıcı iddiayı doğrudan dokümanda kontrol edebilir.

## Ne zaman uygundur?

Hukuki belgeler, sağlık kayıtları, iç şirket wiki'leri ya da fikri mülkiyet içeren teknik dokümanlar gibi dışarı çıkmaması gereken içeriklerde yerel RAG doğal bir tercihtir.
