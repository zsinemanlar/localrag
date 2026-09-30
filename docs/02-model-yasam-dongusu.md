# Model yaşam döngüsü

Foundry Local'da bir model dört aşamadan geçer: katalogdan seçilir, indirilir, belleğe yüklenir ve kullanımdan sonra bellekten çıkarılır.

## Katalog ve alias

Katalogdaki her modelin bir alias'ı vardır. Alias, aynı modelin farklı donanımlar için hazırlanmış varyantlarını tek bir isim altında toplar. Örneğin bir modelin CPU, GPU ve NPU için ayrı varyantları olabilir. Geliştirici sadece alias'ı yazar.

## İndirme ve cache

download çağrısı model dosyalarını yerel cache klasörüne indirir ve ilerleme yüzdesini bir callback ile bildirir. Model daha önce indirildiyse bu adım atlanır. Cache kalıcıdır, yani uygulamayı kapatıp açmak yeniden indirme gerektirmez.

## Yükleme ve bellek

load çağrısı model ağırlıklarını RAM'e (varsa GPU belleğine) alır. Bu adım birkaç saniye sürebilir ve model ne kadar büyükse o kadar bellek tüketir. Kullanım bitince unload ile bellek geri verilir. Model cache'ten silinmez, sadece bellekten çıkar.

## Client'lar

Yüklenen modelden bir client alınır. Chat modelleri için chat client mesaj listesini alıp cevap üretir, isteğe bağlı olarak token token stream eder. Embedding modelleri için embedding client metni bir vektöre çevirir.
