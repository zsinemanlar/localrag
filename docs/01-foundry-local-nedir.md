# Foundry Local nedir?

Foundry Local, yapay zeka modellerini bulut bağlantısı olmadan kendi cihazınızda çalıştırmanızı sağlayan bir Microsoft çözümüdür. Model, uygulamanızın çalıştığı bilgisayarda kalır; istekler ağa çıkmaz, bir API anahtarı ya da abonelik gerekmez.

## Nasıl çalışır?

Foundry Local, modelleri ONNX Runtime üzerinde çalıştırır. Modeller ONNX formatına dönüştürülmüş ve cihaz için optimize edilmiş halde bir katalogda sunulur. Uygulama SDK üzerinden bir model alias'ı ister, örneğin qwen2.5-1.5b, SDK de bu alias için cihaza en uygun variant'ı seçer.

SDK Python, C#, JavaScript ve Rust için sunulur. Python paketi native bir kütüphaneyi süreç içinde yükler, dolayısıyla ayrı bir servis kurmak veya portları yönetmek gerekmez. İnternet bağlantısı yalnızca ilk kullanımda model dosyalarını indirmek için kullanılır. Dosyalar indirildikten sonra uygulama tamamen offline çalışır.

## Nerede işe yarar?

Gizlilik hassasiyeti yüksek verilerde, internetin olmadığı ortamlarda (saha, uçak, izole ağlar) ve kullanım başına ödeme yapmak istemeyen prototiplerde kullanışlıdır. Karşılığında modeller buluttaki büyük modellerden küçüktür; bu yüzden cevap kalitesi model boyutuna ve donanıma bağlıdır.
