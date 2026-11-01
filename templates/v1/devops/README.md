# devops

## 脚本

| 脚本 | 用途 |
| ---- | ---- |
| [mktemp.py](./mktemp.py) | 在 `tmp/<YYYYMMDD>/` 下创建临时文件 |

### mktemp.py

按项目临时文件约定（`tmp/<YYYYMMDD>/`）创建当天的临时文件并输出路径，文件名为当前时刻的 `HHMM.<扩展名>`：

```bash
python3 devops/mktemp.py <extension>   # 例如 html、svg、json
```
