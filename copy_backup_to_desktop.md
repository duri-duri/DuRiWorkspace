# 백업 파일을 바탕화면으로 복사하기

## 📦 백업 파일 복사 명령어

터미널에서 다음 명령어를 실행하세요:

```bash
# 백업 파일을 바탕화면으로 복사
cp DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz ~/Desktop/

# 복사 확인
ls -lh ~/Desktop/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz
```

## 📋 백업 파일 정보

- **파일명**: DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz
- **크기**: 631MB
- **위치**: /home/duri/DuRiWorkspace/
- **복사 대상**: /home/duri/Desktop/

## 🔍 복사 후 확인사항

1. **바탕화면에서 파일 확인**
   ```bash
   ls -lh ~/Desktop/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz
   ```

2. **파일 크기 확인**
   ```bash
   du -h ~/Desktop/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz
   ```

3. **파일 무결성 확인**
   ```bash
   tar -tzf ~/Desktop/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz > /dev/null && echo "복사된 파일 정상" || echo "복사된 파일 오류"
   ```

## 💾 백업 파일 관리

### 현재 위치
- **원본**: /home/duri/DuRiWorkspace/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz
- **복사본**: /home/duri/Desktop/DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz

### 권장사항
1. **원본 유지**: 프로젝트 폴더의 원본은 그대로 두세요
2. **복사본 활용**: 바탕화면의 복사본을 사용하세요
3. **안전한 보관**: 복사본을 외부 저장소에 추가로 백업하세요

## 🎯 다음 단계

백업 파일 복사가 완료되면:

1. **바탕화면에서 파일 확인**
2. **필요시 외부 저장소에 업로드**
3. **복원 테스트 진행** (선택사항)

---

**복사 명령어**: `cp DuRiWorkspace_v1.0.0_final_20250725_124436.tar.gz ~/Desktop/`
**상태**: 복사 대기 중
