import React, { useState, useRef } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

/* ─── 애니메이션 ─── */
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
`;

/* ─── 스타일 ─── */
const Page = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #FAFAF8;
  animation: ${fadeIn} 0.25s ease both;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 52px 16px 12px;
  border-bottom: 1px solid #D0CFC8;
  background: #FAFAF8;
`;

const BackBtn = styled.button`
  width: 36px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  color: #1C1C1A;
  transition: opacity 0.15s;
  &:active { opacity: 0.6; }
`;

const HeaderTitle = styled.h2`
  font-size: 17px;
  font-weight: 700;
  color: #1C1C1A;
  letter-spacing: -0.3px;
`;

const HeaderSpacer = styled.div`
  width: 36px;
`;

const Body = styled.div`
  flex: 1;
  padding: 24px 20px;
  overflow-y: auto;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
`;

const Subtitle = styled.p`
  font-size: 18px;
  font-weight: 700;
  color: #1C1C1A;
  margin-bottom: 20px;
  letter-spacing: -0.4px;
`;

/* 이미지 박스 */
const ImageBox = styled.div`
  width: 100%;
  aspect-ratio: 1;
  background: #F0EFEA;
  border-radius: 12px;
  border: 1.5px solid #D0CFC8;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  transition: border-color 0.15s;
  &:hover { border-color: var(--color-primary); }
`;

const SelectedImg = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
`;

const Placeholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
`;

const DiagLine = styled.div`
  position: absolute;
  width: 90%;
  height: 1px;
  background: #D0CFC8;
  transform: ${p => p.right ? 'rotate(-45deg)' : 'rotate(45deg)'};
`;

const InnerBorder = styled.div`
  position: absolute;
  inset: 12px;
  border: 1px solid #D0CFC8;
  border-radius: 4px;
`;

const PlaceholderHint = styled.p`
  position: absolute;
  font-size: 13px;
  font-weight: 700;
  color: #9E9D96;
  bottom: 20px;
  width: 100%;
  text-align: center;
`;

/* 하단 행 */
const Row = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
`;

const RecentBtn = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font);
  font-size: 14px;
  font-weight: 600;
  color: #5E5E5A;
  padding: 4px 0;
  transition: color 0.15s;
  &:hover { color: var(--color-primary); }
`;

const SelectBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  background: #EBF5EC;
  border: 1px solid #C5DEC7;
  border-radius: 8px;
  cursor: pointer;
  font-family: var(--font);
  font-size: 14px;
  font-weight: 700;
  color: #3A7D44;
  transition: background 0.15s;
  &:active { background: #C5DEC7; }
`;

/* 푸터 */
const Footer = styled.div`
  padding: 12px 20px calc(12px + env(safe-area-inset-bottom));
  background: #FAFAF8;
`;

const SubmitBtn = styled.button`
  width: 100%;
  padding: 17px;
  background: ${p => p.disabled ? '#F0EFEA' : '#3A7D44'};
  color: ${p => p.disabled ? '#9E9D96' : '#FFFFFF'};
  border: none;
  border-radius: 12px;
  font-family: var(--font);
  font-size: 16px;
  font-weight: 700;
  cursor: ${p => p.disabled ? 'default' : 'pointer'};
  letter-spacing: -0.3px;
  box-shadow: ${p => p.disabled ? 'none' : '0 4px 16px rgba(58,125,68,0.3)'};
  transition: all 0.15s;
  &:active { opacity: ${p => p.disabled ? 1 : 0.88}; }
`;

/* 숨긴 파일 input */
const HiddenInput = styled.input`
  display: none;
`;

/* ─── 컴포넌트 ─── */
export default function Authorize({ onBack, onSubmit }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setSelectedImage(url);
  };

  const openGallery = () => fileInputRef.current?.click();

  const handleSubmit = () => {
    if (!selectedImage) {
      alert('인증할 사진을 선택해주세요.');
      return;
    }
    // TODO: API 연동 — FormData로 이미지 업로드
    setSubmitted(true);
    onSubmit?.();   // 부모(MatchingRoom)에게 완료 알림 (상태 업데이트)
  };

  const handleChangePhoto = () => {
    setSubmitted(false);
    setSelectedImage(null);
    setTimeout(() => fileInputRef.current?.click(), 50);
  };

  return (
      <Page>
        {/* ── 헤더 ── */}
        <Header>
          <BackBtn onClick={onBack}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <path d="M14 17L8 11L14 5" stroke="currentColor" strokeWidth="2.2"
                    strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </BackBtn>
          <HeaderTitle>인증</HeaderTitle>
          <HeaderSpacer />
        </Header>

        {/* ── 본문 ── */}
        <Body>
          <Subtitle>{submitted ? '인증 대기 중입니다..' : '오늘의 실천을 인증해주세요.'}</Subtitle>

          {/* 이미지 선택 영역 */}
          <ImageBox onClick={submitted ? undefined : openGallery} style={{ cursor: submitted ? 'default' : 'pointer' }}>
            {selectedImage ? (
                <>
                  <SelectedImg src={selectedImage} alt="선택된 인증 사진" />
                  {submitted && (
                      <div style={{
                        position: 'absolute', inset: 0,
                        background: 'rgba(0,0,0,0.35)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexDirection: 'column', gap: 10,
                      }}>
                        <div style={{
                          background: 'rgba(255,255,255,0.92)',
                          borderRadius: 40, padding: '10px 22px',
                          fontSize: 15, fontWeight: 800, color: '#2E7D32',
                          display: 'flex', alignItems: 'center', gap: 8,
                        }}>
                          <span>⏳</span> 인증 검토 중
                        </div>
                      </div>
                  )}
                </>
            ) : (
                <Placeholder>
                  <DiagLine />
                  <DiagLine right />
                  <InnerBorder />
                  <PlaceholderHint>사진을 탭해서 선택하세요</PlaceholderHint>
                </Placeholder>
            )}
          </ImageBox>

          {/* 최근 항목 / 선택 버튼 — 제출 전에만 표시 */}
          {!submitted && (
              <Row>
                <RecentBtn onClick={openGallery}>최근 항목 ›</RecentBtn>
                <SelectBtn onClick={openGallery}>
                  <span style={{ fontSize: 15 }}>⊞</span>
                  선택
                </SelectBtn>
              </Row>
          )}
        </Body>

        {/* ── 작성 완료 ── */}
        <Footer>
          {submitted ? (
              <SubmitBtn onClick={handleChangePhoto}>
                사진 변경
              </SubmitBtn>
          ) : (
              <SubmitBtn disabled={!selectedImage} onClick={handleSubmit}>
                작성 완료
              </SubmitBtn>
          )}
        </Footer>

        {/* 숨긴 파일 input */}
        <HiddenInput
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
        />
      </Page>
  );
}