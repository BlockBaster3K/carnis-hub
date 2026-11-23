# Carnis — Gate A: передача исходных 35 текстур блоков

**Состояние: передано на Gate A, решение заказчика не получено.** Это 14 баз ТЗ‑1 и 21 вариант ТЗ‑2, не утверждение о завершении мобов B017/B018/B019. Новая ревизия биохоррора ведётся отдельно на основе репозитория 3.4.10.

## Состав и проверка

- 35 PNG в `textures/block/`; каждый 16×16, RGBA, alpha=255.
- 35 автономных скриптов перерисовали файлы побайтно по пикселям; для 21 варианта повторно проверены палитры и точные повороты/зеркала/сдвиги. Проверка автоматическая, не визуальная приёмка.
- ТЗ‑1 заявлено готовым к интеграции; по ТЗ‑2 предыдущий отчёт прямо отмечает оставшиеся визуальные замечания: повторы, концентрические мотивы на нервных торцах, квадратные формы и полосатость. 21 вариант, а не 19.
- Принято заказчиком: использование плоской `flesh_veins` без торцов; разрешены дополнительные промежуточные тона ТЗ‑1. Не утверждаем, что все варианты уже прошли Gate A.

## Несовпадение с пакетом 3.4.10

- Сверено с `BlockBaster3K/carnis-hub` main, commit `a0ec7369de21ec6a4f86260ac7f4d2c2219c2a0e`, архив `01-coder/project-3.4.10-clean.zip`. В его рабочем дереве 51 PNG блока.
- Из 35 сдаваемых имён только 6 совпадают с именами PNG 3.4.10; все шесть отличаются по байтам, а `nerve_pillar.png` и `sinew_spikes.png` отличаются и по размерам: 16×16 в сдаче против 16×64 в 3.4.10. Остальные 29 имён отсутствуют в дереве 3.4.10. **Не копировать пакет поверх 3.4.10 без адаптации имён, анимаций и форматов.**
- Работа над хоррор-ревизией выполняется по настоящим именам и спецификации файлов 3.4.10. Девять файлов сердца LOCK не изменять.

## Отдельно — ТЗ‑3 rev3.1 по мобам

Ранее под rev3.1 находились B017/B018/B019. Рабочие GLB не прошли полную проверку видимых границ и визуального чек-листа. Текущая передача 35 блоков **не является сдачей этих мобов**, не закрывает их блокеры и не заменяет Gate A. См. `analysis_rev31/STATUS_рабочий_без_сдачи.md`. Minecraft/GeckoLib не проверялись.

## Манифест: относительный путь, байты, SHA-256

- `textures/block/bone_flesh.png` · 381 байт · `b8873c7ed4ea27b12c28445419e98e214758ec4c822ca6711ccd956ad7a0008a`
- `textures/block/bone_flesh_1.png` · 323 байт · `9f4e3d12848e6c64590b3404ec5d91d8dacd0b33f3db786cd8e9c96a4bb72528`
- `textures/block/charred_flesh.png` · 411 байт · `f1218ab711b1dd83c2f72a0cb4cb63401b21483066c5ef349da9a4d1313429eb`
- `textures/block/charred_flesh_1.png` · 311 байт · `1b9ff53743bb2c13e25f0c4b7a5d4b56bb2f6a3fd8e7c7a3b57208405a0c9984`
- `textures/block/flesh_block.png` · 392 байт · `e837f911f3deb96c4af160cff6170b449092fdab14a3bc24caf4a0706d008587`
- `textures/block/flesh_block_1.png` · 330 байт · `852d9bcc676b57ee2e19c6becfb58223ddfb0a431012ffa0ff882854e89742bc`
- `textures/block/flesh_block_2.png` · 313 байт · `053779f48eabbef621692b47034f170c78e5228ffa7531b031e74384b98faaa6`
- `textures/block/flesh_block_3.png` · 324 байт · `9edc6d36fe92da8d04385a81e5d4b3713f236344adde2551820ed3a0e71bf7ab`
- `textures/block/flesh_veins_t1.png` · 408 байт · `f7fab70a35094784d144371adec97e8ae8ed8b3ee2d11579536f136a89e36a5a`
- `textures/block/flesh_veins_t1_1.png` · 326 байт · `3cbcb82d14d644ce418aa1dda71e3f79e9d58ac7a87957ec387c87cb452e49e6`
- `textures/block/flesh_veins_t1_2.png` · 303 байт · `1219eb6fef6e741d6663bb5b6a25cd425d86e1bfd9af5ee06202a7d1498c7d5e`
- `textures/block/flesh_veins_t2.png` · 418 байт · `6743d184fb2f42eb35ce5be8523993d0eff0c85e4568e1e2d7c1e1faf56a0f1f`
- `textures/block/flesh_veins_t2_1.png` · 327 байт · `fe5703befc3030a455a8edccd3025449524f56b276968df3d2b693447f867bed`
- `textures/block/flesh_veins_t2_2.png` · 345 байт · `3c1f4172f803e135551b0edff0bb0286e44695aaacfa9374542624d66f2138cb`
- `textures/block/flesh_veins_t3.png` · 450 байт · `c44cf2017626be10e89ec6bc42e6392f287a252eb6abe0009fc327c77afdf8f5`
- `textures/block/flesh_veins_t3_1.png` · 355 байт · `910ab7a5a10b00d06f0102508099dd38bcb4291ec3dbb473fd1f914918f7ed25`
- `textures/block/flesh_veins_t3_2.png` · 373 байт · `aa475eed12d6d315f3e65b3242108c9d5bd4f48d7a3141c057ca77c6ebdce1e7`
- `textures/block/flesh_veins_t4.png` · 492 байт · `459c4cf6928e8bc5d684f00cd64f3a7df1da88211dc36f391662f0d1c124b65b`
- `textures/block/flesh_veins_t4_1.png` · 372 байт · `d549f68b6aa8485357a334ff77f440496c1009c09bcc99cf2038c36a6a007f2f`
- `textures/block/flesh_veins_t4_2.png` · 328 байт · `baf0f58885db08f463afd150661f484779cf811f724ace188e3cab657d13d0e1`
- `textures/block/nerve_pillar.png` · 287 байт · `a1d3353a8fda7e50e30cf6108152b22cb14c3e51a4700894e7ac6a5096a22e76`
- `textures/block/nerve_pillar_1.png` · 255 байт · `8db1cce4f86d99a77054926d57e916140f11ce2784669d574b6d7a531a4de4a1`
- `textures/block/nerve_pillar_2.png` · 276 байт · `0d673fdc2cfbfb4b19edf2f54c9e1945b89fa00c6297718115bcc43217e02008`
- `textures/block/nerve_pillar_top.png` · 318 байт · `191d08e4469dd66d3245881f5ac85248f557948e1c6894196c292319b973266a`
- `textures/block/nerve_pillar_top_1.png` · 289 байт · `9e84760d78e030171fa6bd7fb7486cb47b8614a1c833e0bef6c1aa1b9eaed5a5`
- `textures/block/nerve_pillar_top_2.png` · 315 байт · `69c161881d6b5b65ccc4c4d826ca3dc2a73074f87f1220ea3d9ae16ab9977168`
- `textures/block/refractory_flesh.png` · 290 байт · `0bdc9971bbf521826d423663efe419a2c7a6d7504e1b2920a3ed46ca79a50812`
- `textures/block/refractory_flesh_1.png` · 274 байт · `a6126688eee97f3efeb70339ffc8235054b70fe172e2fc3bd22f34d69a1df189`
- `textures/block/sinew_spikes.png` · 334 байт · `7483a39f9bce15c81da5d570b1fa6ce3bd5f1ad038b11ca498a52e3ca73e7831`
- `textures/block/sinew_spikes_1.png` · 299 байт · `b50a1ebf90aa02a0235d3cf84bebbe3e99b20640dd69054d7e16f45f82b22a59`
- `textures/block/stomach_pool_bottom.png` · 307 байт · `7735ef963d8c321e15c8b814b26459c7407c80f9957b2b1ff00702790ce1fd7c`
- `textures/block/stomach_pool_side.png` · 304 байт · `60548f4d4d3662d912fa2fe63fb0ca37452e1293f91b0c1205be561e89c25da3`
- `textures/block/stomach_pool_side_1.png` · 274 байт · `9d0cc88cf34eebab226df1c71f15a756fee44868379254a94340660caf1dbd36`
- `textures/block/stomach_pool_top.png` · 327 байт · `2adbbef69a0af62df2ce76f5b3fb63841684424560726a36cd99f5f7cf464f8f`
- `textures/block/stomach_pool_top_1.png` · 309 байт · `e27e2efb7318a84f66e185e5a7cef6c7963bb6d8b1ce4ebb2d909d66b05e8956`
