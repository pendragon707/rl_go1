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

Придется переключиться на стороннюю ветку (временная мера, пока не починю основную ветку): 
```
git switch plots  
```

2. Копируем в `rl_go1/src` директорию с обученными моделями

3. В файле `src/policy_copy.py` изменяем пути к моделям на новые, если названия изменились

```
    prop_enc_pth = 'src/models/prop_encoder_1200.pt'
    mlp_pth = 'src/models/mlp_1200.pt'
    mean_file = 'src/models/mean1200.csv'
    var_file = 'src/models/var1200.csv'
```

4. Запускаем из директории `rl_go1`:

```
python src/policy_copy.py --real --aliengo
```
