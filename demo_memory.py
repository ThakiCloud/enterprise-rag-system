#!/usr/bin/env python3
"""
메모리 기능 데모 스크립트

이 스크립트는 Enterprise RAG System의 새로운 메모리 기능을 데모하기 위한 것입니다.
agno 기반 메모리 시스템이 어떻게 작동하는지 보여줍니다.

사용법:
    python demo_memory.py

요구사항:
    - backend 서버가 실행 중이어야 합니다 (python run_backend.py)
    - 환경 변수에 API 키가 설정되어 있어야 합니다
"""

import requests
import json
import time
from typing import Dict, Any

class MemoryDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = "demo_session_001"
        self.user_id = "demo_user"
        
    def make_request(self, endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
        """API 요청을 보내고 응답을 반환합니다."""
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            return {"error": str(e)}
    
    def query_with_memory(self, question: str) -> Dict[Any, Any]:
        """메모리를 활용한 질문을 보냅니다."""
        data = {
            "question": question,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "use_memory": True
        }
        
        print(f"🤔 질문: {question}")
        result = self.make_request("/query/", method="POST", data=data)
        
        if "error" not in result:
            print(f"✅ 답변: {result.get('answer', 'No answer field')}")
            print(f"💾 메모리 업데이트: {result.get('memory_updated', False)}")
            print(f"📊 메모리 개수: {result.get('memory_count', 0)}")
        else:
            print(f"❌ 오류: {result['error']}")
        
        print("-" * 50)
        return result
    
    def get_memories(self) -> Dict[Any, Any]:
        """현재 저장된 메모리를 조회합니다."""
        print("📋 현재 저장된 메모리 조회:")
        result = self.make_request(f"/sessions/{self.session_id}/memories")
        
        if "error" not in result:
            memories = result.get("memories", [])
            if memories:
                for i, memory in enumerate(memories, 1):
                    print(f"  {i}. {memory.get('memory', 'No content')}")
                    print(f"     주제: {', '.join(memory.get('topics', []))}")
                    print(f"     생성일: {memory.get('created_at', 'Unknown')}")
                    print()
            else:
                print("  저장된 메모리가 없습니다.")
        else:
            print(f"❌ 오류: {result['error']}")
        
        print("-" * 50)
        return result
    
    def search_memories(self, query: str) -> Dict[Any, Any]:
        """특정 키워드로 메모리를 검색합니다."""
        print(f"🔍 메모리 검색: '{query}'")
        data = {"query": query, "limit": 5}
        result = self.make_request(f"/sessions/{self.session_id}/search-memories", method="POST", data=data)
        
        if "error" not in result:
            memories = result.get("memories", [])
            print(f"  검색 결과: {len(memories)}개 발견")
            for i, memory in enumerate(memories, 1):
                print(f"    {i}. {memory.get('memory', 'No content')}")
        else:
            print(f"❌ 오류: {result['error']}")
        
        print("-" * 50)
        return result
    
    def add_manual_memory(self, content: str, topics: list = None) -> Dict[Any, Any]:
        """수동으로 메모리를 추가합니다."""
        print(f"➕ 수동 메모리 추가: {content}")
        data = {
            "action": "add",
            "memory_content": content,
            "topics": topics or []
        }
        result = self.make_request(f"/sessions/{self.session_id}/memories", method="POST", data=data)
        
        if "error" not in result:
            print(f"✅ 메모리 추가 완료 (ID: {result.get('memory_id', 'Unknown')})")
        else:
            print(f"❌ 오류: {result['error']}")
        
        print("-" * 50)
        return result
    
    def clear_memories(self) -> Dict[Any, Any]:
        """모든 메모리를 삭제합니다."""
        print("🗑️ 모든 메모리 삭제...")
        data = {"action": "clear"}
        result = self.make_request(f"/sessions/{self.session_id}/memories", method="POST", data=data)
        
        if "error" not in result:
            print("✅ 모든 메모리가 삭제되었습니다.")
        else:
            print(f"❌ 오류: {result['error']}")
        
        print("-" * 50)
        return result
    
    def run_demo(self):
        """전체 데모를 실행합니다."""
        print("🧠 Enterprise RAG System - 메모리 기능 데모")
        print("=" * 60)
        print(f"세션 ID: {self.session_id}")
        print(f"사용자 ID: {self.user_id}")
        print("=" * 60)
        
        # 1. 초기 메모리 상태 확인
        print("1️⃣ 초기 상태 확인")
        self.get_memories()
        
        # 2. 사용자 정보 수집
        print("2️⃣ 사용자 정보 수집")
        self.query_with_memory("안녕하세요, 저는 김철수이고 Python 개발자입니다.")
        time.sleep(1)
        
        self.query_with_memory("저는 머신러닝에 관심이 많고, 특히 자연어처리를 공부하고 있습니다.")
        time.sleep(1)
        
        # 3. 메모리 확인
        print("3️⃣ 수집된 메모리 확인")
        self.get_memories()
        
        # 4. 컨텍스트 기반 대화
        print("4️⃣ 컨텍스트 기반 대화")
        self.query_with_memory("제가 관심있는 분야와 관련된 책을 추천해주세요.")
        time.sleep(1)
        
        self.query_with_memory("제 이름을 기억하시나요?")
        time.sleep(1)
        
        # 5. 메모리 검색
        print("5️⃣ 메모리 검색 테스트")
        self.search_memories("개발자")
        self.search_memories("머신러닝")
        
        # 6. 수동 메모리 추가
        print("6️⃣ 수동 메모리 추가")
        self.add_manual_memory("사용자는 Flask 웹 프레임워크를 선호합니다", ["웹개발", "Flask"])
        
        # 7. 업데이트된 메모리 확인
        print("7️⃣ 업데이트된 메모리 확인")
        self.get_memories()
        
        # 8. 새로운 컨텍스트로 대화
        print("8️⃣ 새로운 컨텍스트로 대화")
        self.query_with_memory("웹 개발 프레임워크 중에서 추천해주실 만한 것이 있나요?")
        
        # 9. 메모리 정리 (선택적)
        print("9️⃣ 메모리 정리 (데모 종료)")
        user_input = input("모든 메모리를 삭제하시겠습니까? (y/N): ")
        if user_input.lower() == 'y':
            self.clear_memories()
            self.get_memories()
        
        print("🎉 메모리 기능 데모가 완료되었습니다!")
        print("이제 UI에서도 동일한 세션으로 대화를 계속할 수 있습니다.")

def main():
    """메인 함수"""
    print("서버 연결 확인 중...")
    
    demo = MemoryDemo()
    
    # 서버 상태 확인
    try:
        response = requests.get(f"{demo.base_url}/docs")
        response.raise_for_status()
        print("✅ 백엔드 서버가 실행 중입니다.")
    except requests.exceptions.RequestException:
        print("❌ 백엔드 서버에 연결할 수 없습니다.")
        print("먼저 'python run_backend.py'로 서버를 실행해주세요.")
        return
    
    # 데모 실행
    demo.run_demo()

if __name__ == "__main__":
    main() 