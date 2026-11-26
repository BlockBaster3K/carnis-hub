# Кодер — T-3171: пересборка 3.7.2 из текущего банка

- **Статус:** выполнено.
- **База:** пакет после T-3166, ZIP SHA-256 `c271d30af7b6b6d83c4dcf68dbc08ab2e999e674ea53895070582056fa4e9989`.
- **Обновление:** ровно 15 `.ogg` заменены побайтово содержимым актуального `03-sound/sounds/`; перекодирования не было.
- **Дельта:** 15 файлов изменились; остальные **744 из 759** совпали побайтово с предыдущим ZIP, включая `incubation_cyst.png`.
- **Звуки:** 144/144 `.ogg` в новом ZIP совпадают с текущим банком.
- **Гейт:** `python3 tools/accept_3.7.2.py` → код 0, `ИТОГ: ПРИНЯТО`; все 759 записей манифеста проверены.
- **Новый ZIP:** 12 605 693 байта; SHA-256 `362bdda2e3aaa0a9450fdf6bb6bede014af612d1efd92cf84ab0e074b8ccab63`.
- **Манифест:** 759 строк; SHA-256 `2f40e0579401cc48d412d50b14bff8fb144b1a88205250fcf6fc309987b01cc5`.

| Файл | SHA-256 до | SHA-256 после (банк) |
|---|---|---|
| `combat_deflect_01_chitin.ogg` | `89a3198b22634b4f77605e87fd8a2d268b1be122ded1866f6c809213d2cf550d` | `737ddee7079aae228c2d141247340e7fdd1be03cad6ccd5f81e55fcfb607d1f5` |
| `combat_deflect_02_bone.ogg` | `057b7508b319f6d2552abf77c5bcf3b2128720646b2222ca654c52567863c8a0` | `f3889a821d46a2274a242e99883944c56576c5da53bd2af57f6c72d87c979814` |
| `combat_deflect_03_metal.ogg` | `f3f4a85af6ab90fa23f049623ce4518a64ef14ea83092d0fc541f3335c85b427` | `e8ea502ddbf94770a4f9002acdb066e323c902e307adbac2b5ef5f15abc1c0ac` |
| `combat_deflect_04_glance.ogg` | `a8c233e1f630a7dd6b7c2d30e2292ce261c194ce8f9db1c86e3b5c495c355a46` | `af2bd3c07e46ba48c44c0749508fb0685ea0e5113038d524bf3c9d15a8e6526d` |
| `combat_deflect_05_parry.ogg` | `fb45cc40da3277ef310ab41e936128f8cd4163f32f861a5cddc33676ef365a76` | `63f6301bbf940db477492081c69dbc21adb93afa24fca2f62e71567d9b86a990` |
| `combat_flesh_hit_deep_01_axe.ogg` | `a4559a5ade8265a52c253d168c0c67df8bcd3ec93f17ccd0a8d869d492006f4c` | `1ab864ae2b474adf87999946b19cf7bd8f4fe61424a511ef538b9d39b472fe08` |
| `combat_stab_01_bone.ogg` | `791a754302eccc9f52b45092bb3ef032c3612b2884e278d39ecd7e2daa509a05` | `4f54cea99cacea2ce74e274c9b6d50b900bfee8652c4474e3401ddbc443e598d` |
| `combat_stab_02_chitin.ogg` | `3d7cbea63a4269cf9ffdfca1430607ca9aba87d2e4bfed731b9a8d4fdaa871fc` | `b6292a8eb9cf73b74e43bcfe72227cacca9824cee59b5a5416cbbfb0f5ebf33e` |
| `combat_stab_03_shield.ogg` | `151444b93864788168eb19ec66153fa02aea19625f08ac82a3b0cf8ec301ab30` | `735ec65e3cf8c4b532105ae45a5186dc1102d11bf19718212f4791204056b1cc` |
| `dismember_01.ogg` | `2301278a6c76ffa918be900440d8c06df66c1abf6061b2edce49642793682c50` | `a5f4f66837382f1335b3bb1cf96ae6f5c83744afe2916b3d968ae8079e603306` |
| `flesh_block_step_01.ogg` | `9deaa524c313eeee0e2a8e911d338d432ec30f20bd10457f66238c09995a1124` | `dca41b8b80344a7794a3fb438749de4436e7241931769609ca507df72f217410` |
| `hive_spawn_attack_02.ogg` | `a3c3c1d1afdcbcb6ae7ebf80e2a8b838ea360b76006f3cedc64e3c7248fe57e0` | `778321eb8f87c75bbd8f80a7cdc2722598737609194f9e91b179476eb9a3351e` |
| `hive_spawn_hurt_01.ogg` | `6bb4ae17cac416ecab8d3efe4bf4365ef9c719a97abd0c6af277d57cf43300e4` | `d6e28d2a2fbeb930e9bdc9b8965935d46bc80ac28b5687aaa2a94241b4cfbdc2` |
| `hive_spawn_hurt_04.ogg` | `5c538da8ddbd27965d8bda3ae060ebab7943e9319f6209a51fbe07c8a6eb50fc` | `9e403e4782949b8627233142608d07098b88b8e39f73f672898567ed0bcd83e3` |
| `hive_spread_01_creep.ogg` | `cf214ce8d38b4e59df92fc63a36633772a3c3f5905de4ae473ba86399ac39425` | `6df4b50edbf1d3bddfc968cfd0870b78eb5ee68564ca6cf836eac675b03576e7` |

ZIP/манифест обновлены; тег и релиз не создавались.
