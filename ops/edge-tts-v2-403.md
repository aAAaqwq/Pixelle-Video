# Edge-TTS 403 修复与部署验收

## 原因与范围

微软语音服务拒绝旧版 Sec-MS-GEC v1 握手。将 `edge-tts` 从
`7.2.7` 固定升级至 `7.3.1`，使用上游提供的 v2 协议实现；不手改
鉴权算法，不切换服务商，不升级其他依赖。

依赖声明与 `uv.lock` 必须同时更新。离线回归检查同时约束声明、锁文件、
实际安装库的协议版本和 token 格式；不向微软或付费数字人服务提交请求。

## 本地验收

```sh
uv sync --locked --extra dev
uv run --no-sync python -m pytest -q
uv run --no-sync ruff check tests/test_edge_tts_dependency.py
uv lock --check
git diff --check
```

在线握手成功不等于音频或数字人生成成功。获准在线验收后应使用非敏感
固定测试文案，检查音频字节非空，并以 ffprobe 验证音频可解码；完整数字人
验收另需测试素材和付费额度，不得擅自重放用户失败任务或扣费。

## 生产部署与回退约束

1. PR 审查、CI 完成后，核对待部署提交和授权范围。记录运行服务、旧版
   依赖、当前清单及其校验值。不要把服务器源码副本当作远端 Git 基线。
2. 线上含未提交的数字人定制代码：**禁止整仓覆盖、强制重置或全量依赖
   升级**。仅同步本次已审查的依赖清单改动；保留其他代码、配置和数据。
3. 在私有回退目录备份现有 `pyproject.toml`、`uv.lock`、Edge-TTS 包及其
   dist-info/CLI，以及项目可编辑安装的 dist-info 和路径文件，准备旧版
   wheel。备份可能含源码，不对外发布。
4. 从锁文件取得 `7.3.1` wheel 并验证 SHA-256，在隔离环境验证 v2 协议
   和音频合成。由现有虚拟环境创建的嵌套 venv 不会自动继承该环境的
   第三方依赖；隔离预验收需明确提供依赖，避免误判缺包为升级失败。
5. 确认无运行中或待执行任务后，在维护窗口停止受影响的 Pixelle 进程。
   同步定向依赖清单改动，再用现有 uv 对指定虚拟环境安装已校验的
   wheel，使用 `--no-deps` 避免连带更新。还须重新生成项目的可编辑
   安装元数据：仅修改清单不会更新已安装包中的 `Requires-Dist`。

   ```sh
   /root/.local/bin/uv pip install --python /opt/Pixelle-Video/.venv/bin/python \
     --no-deps --reinstall-package pixelle-video --editable /opt/Pixelle-Video
   /root/.local/bin/uv pip check --python /opt/Pixelle-Video/.venv/bin/python
   ```

6. 依赖检查通过后启动受影响的 Pixelle 进程。该虚拟环境也被 Web UI
   使用，核对实际影响范围，不重启 Super-AIGC 容器或其他项目。验证
   `/health`、Web 健康、语音 API、Super-AIGC 调用链和脱敏错误日志。
7. 任一步失败，恢复清单、旧包和项目安装元数据，再启动受影响服务并
   验证依赖及健康状态。回退 `7.2.7` 只能恢复升级前环境，**不能保证
   解除旧协议的 403**；如仍失败应报告服务降级状态，不循环重试或
   改动其他网络/鉴权配置。

以上命令及步骤仅为运维参考，不构成后续任务的部署授权。

## 2026-10-14 紧急恢复记录（北京时间）

本次用户明确要求先恢复线上功能、后更新仓库，因此部署先于本 PR。
约 08:54 完成定向升级并重启 Pixelle API/Web；未重启 Super-AIGC 容器。

- 升级前运行中、待执行任务均为 0；旧 wheel、清单及安装元数据已备份。
- 第一轮依赖检查发现项目安装元数据仍固定 `7.2.7`，自动回退后，补齐
  可编辑安装元数据重建，再完成升级；最终 145 个已安装包依赖兼容。
- Pixelle 语音 API 返回 17,856 字节、2.976 秒 MP3；Super-AIGC worker
  实际调用返回 15,984 字节 MP3；均经 ffprobe 验证为 24 kHz 单声道。
- 92 个业务代码及配置文件的升级前后 SHA-256 一致。API/Web 健康检查
  正常，检查时重启后握手错误为 0；未执行付费的完整数字人视频生成。
- systemd 有既存的单元配置待重载提示，本次未处理，避免改变无关配置。

上述结果是本次验收记录，不代表后续运行不会遇到新的上游服务变化。
