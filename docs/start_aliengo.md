## Как запустить обученную политику на Aliengo

1. Склонировать форк проекта rl_go1 и выполнить его readme

```
git clone git@github.com:pendragon707/rl_go1.git
```

Особенно не забывайте про эту часть readme:

```
git submodule update --init --recursive
pip install -e submodules/free-dog-sdk/
```

2. Копируем в `rl_go1/models` директорию с обученными моделями

3. В файле `scripts/policy.py` изменяем пути к моделям на новые, если названия изменились

```
    prop_enc_pth = 'src/models/dir/prop_encoder_1200.pt'
    mlp_pth = 'src/models/dir/mlp_1200.pt'
    mean_file = 'src/models/dir/mean1200.csv'
    var_file = 'src/models/dir/var1200.csv'
```

4. Запускаем из директории `rl_go1`:

```
python scripts/policy.py --real --aliengo
```
