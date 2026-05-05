import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()
#extraemos la configuracion 
PORT = int(os.getenv("APP_PORT", 8006))
HOST = "127.0.0.1"
if __name__ == "__main__":
    print("\n" + "="*50)
    print("\033[96m🚀 MS-ANALYTICS: INICIANDO SERVIDOR\033[0m")
    print(f"\033[94m🏠 Host:\033[0m {HOST}")
    print(f"\033[94m🔌 Puerto:\033[0m {PORT}")
    print(f"\033[92m📖 Documentación:\033[0m http://{HOST}:{PORT}/docs")
    print("="*50 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT, reload=True)