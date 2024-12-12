# run.py
import os
import sys
# 將專案根目錄加入 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project.main import main

if __name__ == "__main__":
    import asyncio
    
    if os.name == 'nt':
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )
    
    asyncio.run(main())