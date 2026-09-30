# Donanım ve variant seçimi

Aynı model farklı donanımlarda farklı hızlarda çalışır. Foundry Local bu yüzden bir modelin birden fazla variant'ını tutar ve cihazda hangisinin kullanılabileceğine kendisi karar verir.

## Execution provider'lar

ONNX Runtime, hesaplamayı execution provider (EP) denen arka uçlara yaptırır. CPU her cihazda vardır. NVIDIA ekran kartları için CUDA, Windows'ta çeşitli GPU ve NPU'lar için DirectML ve Windows ML tabanlı provider'lar, Qualcomm ve Intel NPU'ları için ise kendi provider'ları kullanılır. Bir provider kayıtlı değilse o donanıma ait variant seçilemez. Bu yüzden SDK, model seçiminden önce eksik provider'ları indirip kaydetme adımı sunar.

## Seçim sırası

Genel olarak öncelik NPU'da, sonra GPU'da, en son CPU'dadır. NPU düşük güç tüketimiyle yapay zeka işine özelleşmiştir, GPU yüksek hız sağlar, CPU ise her yerde çalışan yedektir. Cihazda hızlandırıcı yoksa ya da provider kaydedilemezse sistem sessizce CPU variant'ına düşer ve uygulama yine çalışır, sadece daha yavaş olur.

## Pratik sonuç

Uygulama kodunda donanıma özel bir dal yazmaya gerek yoktur. Aynı kod bir geliştirici dizüstü bilgisayarında, GPU'lu bir iş istasyonunda ve NPU'lu bir Copilot+ PC'de değişmeden çalışır.
