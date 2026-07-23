/**

 * 智能体后端地址配置

 *

 * 真机 USB 调试：

 * 1) adb reverse tcp:8000 tcp:8000  → 使用下方默认 127.0.0.1

 * 2) 或与电脑同一局域网，开发时临时改 DEFAULT_BASE 为电脑 IP

 *    （后端需 --host 0.0.0.0）

 *

 * 自建后端说明（开源，需自备 API Key）：

 * https://github.com/tuoxingwanli/SCUT-Helper-Agent

 */

const DEFAULT_BASE = 'http://127.0.0.1:8000'



/** 后端自建说明文档（连不上时提示用户） */

export const AGENT_SETUP_DOCS_URL =

  'https://github.com/tuoxingwanli/SCUT-Helper-Agent'



/** 始终使用默认地址，避免历史 storage 覆盖导致连错 */

export function getAgentBaseUrl() {

  return DEFAULT_BASE

}



export { DEFAULT_BASE }


