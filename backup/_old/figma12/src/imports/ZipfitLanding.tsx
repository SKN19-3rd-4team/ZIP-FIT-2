import svgPaths from "./svg-rv2vi5nkk8";

function Container() {
  return <div className="absolute h-[694.4px] left-0 top-0 w-[1100px]" data-name="Container" style={{ backgroundImage: "url('data:image/svg+xml;utf8,<svg viewBox=\\\'0 0 1100 694.4\\\' xmlns=\\\'http://www.w3.org/2000/svg\\\' preserveAspectRatio=\\\'none\\\'><rect x=\\\'0\\\' y=\\\'0\\\' height=\\\'100%\\\' width=\\\'100%\\\' fill=\\\'url(%23grad)\\\' opacity=\\\'1\\\'/><defs><radialGradient id=\\\'grad\\\' gradientUnits=\\\'userSpaceOnUse\\\' cx=\\\'0\\\' cy=\\\'0\\\' r=\\\'10\\\' gradientTransform=\\\'matrix(0 -65.042 -65.042 0 550 347.2)\\\'><stop stop-color=\\\'rgba(0,0,0,0)\\\' offset=\\\'0\\\'/><stop stop-color=\\\'rgba(0,0,0,0.03)\\\' offset=\\\'1\\\'/></radialGradient></defs></svg>')" }} />;
}

function Container1() {
  return <div className="absolute blur-3xl filter left-[275px] rounded-[2.68435e+07px] size-[600px] top-[231.46px]" data-name="Container" />;
}

function Container2() {
  return <div className="absolute blur-3xl filter left-[225px] rounded-[2.68435e+07px] size-[600px] top-[-137.06px]" data-name="Container" />;
}

function Container3() {
  return (
    <div className="absolute h-[694.4px] left-0 overflow-clip top-0 w-[1100px]" data-name="Container">
      <Container1 />
      <Container2 />
    </div>
  );
}

function Logo() {
  return (
    <div className="relative shrink-0 size-[96px]" data-name="Logo">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 96 96">
        <g clipPath="url(#clip0_1_1050)" id="Logo">
          <path d={svgPaths.p162d4400} fill="var(--fill-0, white)" id="Vector" />
          <path d={svgPaths.p36baed80} fill="url(#paint0_linear_1_1050)" id="Vector_2" stroke="url(#paint1_linear_1_1050)" strokeLinejoin="round" strokeWidth="3.84" />
        </g>
        <defs>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_1_1050" x1="24" x2="72" y1="19.2" y2="72">
            <stop stopColor="#10B981" />
            <stop offset="1" stopColor="#059669" />
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint1_linear_1_1050" x1="24" x2="72" y1="19.2" y2="72">
            <stop stopColor="#10B981" />
            <stop offset="1" stopColor="#059669" />
          </linearGradient>
          <clipPath id="clip0_1_1050">
            <rect fill="white" height="96" width="96" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Container4() {
  return (
    <div className="absolute content-stretch flex h-[96px] items-start justify-center left-0 top-0 w-[352.825px]" data-name="Container">
      <Logo />
    </div>
  );
}

function Paragraph() {
  return (
    <div className="absolute content-stretch flex h-[31.988px] items-start left-0 top-0 w-[352.825px]" data-name="Paragraph">
      <p className="basis-0 font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal grow leading-[32px] min-h-px min-w-px relative shrink-0 text-[#52525c] text-[24px] text-center">나에게 딱 맞는 집,</p>
    </div>
  );
}

function Heading() {
  return (
    <div className="absolute h-[96px] left-[40.41px] top-[47.99px] w-[271.988px]" data-name="Heading 1">
      <p className="absolute bg-clip-text font-['Arimo:Bold',sans-serif] font-bold leading-[96px] left-[136px] text-[96px] text-[rgba(0,0,0,0)] text-center text-nowrap top-[-9px] tracking-[-1.92px] translate-x-[-50%] whitespace-pre" style={{ WebkitTextFillColor: "transparent", backgroundImage: "linear-gradient(90deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) 100%), linear-gradient(161.323deg, rgb(0, 153, 102) 0%, rgb(0, 201, 80) 50%, rgb(0, 122, 85) 100%)" }}>
        ZIPFIT
      </p>
    </div>
  );
}

function Container5() {
  return (
    <div className="absolute h-[143.988px] left-0 top-[128px] w-[352.825px]" data-name="Container">
      <Paragraph />
      <Heading />
    </div>
  );
}

function Button() {
  return (
    <button className="absolute bg-white content-stretch cursor-pointer flex h-[51.2px] items-center justify-center left-[184px] px-[41.6px] py-[25.6px] rounded-[2.68435e+07px] top-[32px] w-[168.825px]" data-name="Button">
      <div aria-hidden="true" className="absolute border-[1.6px] border-solid border-zinc-200 inset-0 pointer-events-none rounded-[2.68435e+07px]" />
      <p className="font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[24px] relative shrink-0 text-[16px] text-center text-neutral-950 text-nowrap whitespace-pre">더 알아보기</p>
    </button>
  );
}

function Icon() {
  return (
    <div className="absolute left-[72px] size-[16px] top-[4px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="Icon">
          <path d="M3.33333 8H12.6667" id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.33333" />
          <path d={svgPaths.p1d405500} id="Vector_2" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.33333" />
        </g>
      </svg>
    </div>
  );
}

function LandingPage() {
  return (
    <div className="absolute h-[24px] left-[40px] top-[12px] w-[88px]" data-name="LandingPage">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[24px] left-[32.5px] text-[16px] text-center text-nowrap text-white top-[-2.2px] translate-x-[-50%] whitespace-pre">시작하기</p>
      <Icon />
    </div>
  );
}

function Button1() {
  return (
    <div className="absolute bg-gradient-to-r from-[#009966] h-[48px] left-0 overflow-clip rounded-[2.68435e+07px] shadow-[0px_10px_15px_-3px_rgba(0,0,0,0.1),0px_4px_6px_-4px_rgba(0,0,0,0.1)] to-[#00a63e] top-[33.6px] w-[168px]" data-name="Button">
      <LandingPage />
    </div>
  );
}

function Container6() {
  return (
    <div className="absolute h-[83.2px] left-0 top-[303.99px] w-[352.825px]" data-name="Container">
      <Button />
      <Button1 />
    </div>
  );
}

function LandingPage1() {
  return (
    <div className="h-[24px] overflow-clip relative shrink-0 w-full" data-name="LandingPage">
      <div className="absolute inset-[37.5%_20.83%_33.33%_20.83%]" data-name="Vector">
        <div className="absolute inset-[-14.29%_-7.14%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 9">
            <path d="M15 1L8 8L1 1" id="Vector" stroke="var(--stroke-0, #9F9FA9)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Container7() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-0 size-[24px] top-[0.11px]" data-name="Container">
      <LandingPage1 />
    </div>
  );
}

function Button2() {
  return (
    <div className="absolute left-[164.41px] size-[24px] top-[499.19px]" data-name="Button">
      <Container7 />
    </div>
  );
}

function Container8() {
  return (
    <div className="absolute h-[528.788px] left-[373.59px] top-[82.8px] w-[352.825px]" data-name="Container">
      <Container4 />
      <Container5 />
      <Container6 />
      <Button2 />
    </div>
  );
}

function Section() {
  return (
    <div className="h-[694.4px] overflow-clip relative shrink-0 w-full" data-name="Section">
      <Container />
      <Container3 />
      <Container8 />
    </div>
  );
}

function LandingPage2() {
  return (
    <div className="h-[20px] relative shrink-0 w-full" data-name="LandingPage">
      <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[20px] left-[518.26px] text-[#71717b] text-[14px] text-center text-nowrap top-[98.8px] tracking-[0.7px] translate-x-[-50%] uppercase whitespace-pre">Why ZIPFIT</p>
    </div>
  );
}

function Text() {
  return (
    <div className="absolute content-stretch flex h-[64px] items-start left-[419.39px] top-[92px] w-[96px]" data-name="Text">
      <p className="basis-0 bg-clip-text font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal grow leading-[48px] min-h-px min-w-px relative shrink-0 text-[48px] text-[rgba(0,0,0,0)] text-center" style={{ WebkitTextFillColor: "transparent", backgroundImage: "linear-gradient(90deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0) 100%), linear-gradient(90deg, rgb(0, 153, 102) 0%, rgb(0, 166, 62) 100%)" }}>
        집핏
      </p>
    </div>
  );
}

function LandingPage3() {
  return (
    <div className="h-[48px] relative shrink-0 w-full" data-name="LandingPage">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[48px] left-[387.01px] text-[48px] text-center text-nowrap text-zinc-900 top-[95px] translate-x-[-50%] whitespace-pre">왜</p>
      <Text />
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[48px] left-[598.39px] text-[48px] text-center text-nowrap text-zinc-900 top-[95px] translate-x-[-50%] whitespace-pre">인가요?</p>
    </div>
  );
}

function Container9() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] h-[84px] items-start relative shrink-0 w-full" data-name="Container">
      <LandingPage2 />
      <LandingPage3 />
    </div>
  );
}

function LandingPage4() {
  return <div className="absolute h-[232px] left-0 opacity-0 rounded-[24px] top-0 w-[313.325px]" data-name="LandingPage" />;
}

function Icon1() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d={svgPaths.pb007f00} id="Vector" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p1b58ab00} id="Vector_2" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d="M10 9H8" id="Vector_3" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d="M16 13H8" id="Vector_4" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d="M16 17H8" id="Vector_5" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </g>
      </svg>
    </div>
  );
}

function Container10() {
  return (
    <div className="absolute bg-[#d0fae5] content-stretch flex items-center justify-center left-[32px] rounded-[16px] size-[48px] top-[32px]" data-name="Container">
      <Icon1 />
    </div>
  );
}

function Heading2() {
  return (
    <div className="absolute h-[28px] left-[32px] top-[104px] w-[249.325px]" data-name="Heading 3">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[28px] left-0 text-[20px] text-nowrap text-zinc-900 top-[-2.2px] whitespace-pre">복잡한 공고 문서</p>
    </div>
  );
}

function Paragraph1() {
  return (
    <div className="absolute h-[52px] left-[32px] top-[148px] w-[249.325px]" data-name="Paragraph">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[26px] left-0 text-[#52525c] text-[16px] top-[-2.4px] w-[241px]">공공주거 공고는 복잡하고 구조가 달라서, 이해하기 어렵습니다.</p>
    </div>
  );
}

function LandingPage5() {
  return (
    <div className="absolute h-[232px] left-0 top-0 w-[313.325px]" data-name="LandingPage">
      <Container10 />
      <Heading2 />
      <Paragraph1 />
    </div>
  );
}

function Container11() {
  return (
    <div className="absolute h-[232px] left-0 top-[100px] w-[313.325px]" data-name="Container">
      <LandingPage4 />
      <LandingPage5 />
    </div>
  );
}

function LandingPage6() {
  return <div className="absolute h-[232px] left-0 opacity-0 rounded-[24px] top-0 w-[313.337px]" data-name="LandingPage" />;
}

function Icon2() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d="M12 18V5" id="Vector" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p11c39380} id="Vector_2" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p2e947480} id="Vector_3" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p3d7a0320} id="Vector_4" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p2c99ddc0} id="Vector_5" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p1d3ae070} id="Vector_6" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p157a9000} id="Vector_7" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p25258198} id="Vector_8" stroke="var(--stroke-0, #00A63E)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </g>
      </svg>
    </div>
  );
}

function Container12() {
  return (
    <div className="absolute bg-green-100 content-stretch flex items-center justify-center left-[32px] rounded-[16px] size-[48px] top-[32px]" data-name="Container">
      <Icon2 />
    </div>
  );
}

function Heading3() {
  return (
    <div className="absolute h-[28px] left-[32px] top-[104px] w-[249.338px]" data-name="Heading 3">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[28px] left-0 text-[20px] text-nowrap text-zinc-900 top-[-2.2px] whitespace-pre">AI 기반 문서 분석</p>
    </div>
  );
}

function Paragraph2() {
  return (
    <div className="absolute h-[52px] left-[32px] top-[148px] w-[249.338px]" data-name="Paragraph">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[26px] left-0 text-[#52525c] text-[16px] top-[-2.4px] w-[249px]">LLM이 비정형 문서를 읽고, 맥락을 이해하며 질문에 답합니다.</p>
    </div>
  );
}

function LandingPage7() {
  return (
    <div className="absolute h-[232px] left-0 top-0 w-[313.337px]" data-name="LandingPage">
      <Container12 />
      <Heading3 />
      <Paragraph2 />
    </div>
  );
}

function Container13() {
  return (
    <div className="absolute h-[232px] left-[361.32px] top-[100px] w-[313.337px]" data-name="Container">
      <LandingPage6 />
      <LandingPage7 />
    </div>
  );
}

function LandingPage8() {
  return <div className="absolute h-[232px] left-0 opacity-0 rounded-[24px] top-0 w-[313.325px]" data-name="LandingPage" />;
}

function Icon3() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d={svgPaths.pace200} id="Vector" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p3c6311f0} id="Vector_2" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={svgPaths.p3d728000} id="Vector_3" stroke="var(--stroke-0, #009966)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </g>
      </svg>
    </div>
  );
}

function Container14() {
  return (
    <div className="absolute content-stretch flex items-center justify-center left-[32px] rounded-[16px] size-[48px] top-[32px]" data-name="Container">
      <Icon3 />
    </div>
  );
}

function Heading4() {
  return (
    <div className="absolute h-[28px] left-[32px] top-[104px] w-[249.325px]" data-name="Heading 3">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[28px] left-0 text-[20px] text-nowrap text-zinc-900 top-[-2.2px] whitespace-pre">맞춤형 정보 제공</p>
    </div>
  );
}

function Paragraph3() {
  return (
    <div className="absolute h-[52px] left-[32px] top-[148px] w-[249.325px]" data-name="Paragraph">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[26px] left-0 text-[#52525c] text-[16px] top-[-2.4px] w-[240px]">단순 나열이 아닌, 내 조건에 맞는지 분석하고 설명합니다.</p>
    </div>
  );
}

function LandingPage9() {
  return (
    <div className="absolute h-[232px] left-0 top-0 w-[313.325px]" data-name="LandingPage">
      <Container14 />
      <Heading4 />
      <Paragraph3 />
    </div>
  );
}

function Container15() {
  return (
    <div className="absolute h-[232px] left-[722.66px] top-[100px] w-[313.325px]" data-name="Container">
      <LandingPage8 />
      <LandingPage9 />
    </div>
  );
}

function Container16() {
  return (
    <div className="h-[232px] relative shrink-0 w-full" data-name="Container">
      <Container11 />
      <Container13 />
      <Container15 />
    </div>
  );
}

function Section1() {
  return (
    <div className="bg-neutral-50 content-stretch flex flex-col gap-[80px] h-[581px] items-start relative shrink-0 w-[1036px]" data-name="Section">
      <Container9 />
      <Container16 />
    </div>
  );
}

function Heading1() {
  return (
    <div className="absolute h-[48px] left-[102px] top-[187px] w-[896px]" data-name="Heading 2">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[48px] left-[448.63px] text-[48px] text-center text-nowrap text-white top-[-5px] translate-x-[-50%] whitespace-pre">지금 바로 시작하세요</p>
    </div>
  );
}

function Paragraph4() {
  return (
    <div className="absolute h-[28px] left-[214px] top-[267px] w-[672px]" data-name="Paragraph">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[28px] left-[336.19px] text-[#9f9fa9] text-[18px] text-center text-nowrap top-[-0.6px] translate-x-[-50%] whitespace-pre">복잡한 공고 분석부터 자격 확인, AI 상담까지</p>
    </div>
  );
}

function Icon4() {
  return (
    <div className="absolute left-[149.63px] size-[16px] top-[16px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="Icon">
          <path d="M3.33333 8H12.6667" id="Vector" stroke="var(--stroke-0, #18181B)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.33333" />
          <path d={svgPaths.p1d405500} id="Vector_2" stroke="var(--stroke-0, #18181B)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.33333" />
        </g>
      </svg>
    </div>
  );
}

function Button3() {
  return (
    <div className="absolute bg-white h-[48px] left-[459.19px] rounded-[2.68435e+07px] shadow-[0px_20px_25px_-5px_rgba(0,0,0,0.1),0px_8px_10px_-6px_rgba(0,0,0,0.1)] top-[327px] w-[181.625px]" data-name="Button">
      <p className="absolute font-['Arimo:Regular','Noto_Sans_KR:Regular',sans-serif] font-normal leading-[24px] left-[75px] text-[16px] text-center text-nowrap text-zinc-900 top-[9.8px] translate-x-[-50%] whitespace-pre">무료로 시작하기</p>
      <Icon4 />
    </div>
  );
}

function Section2() {
  return (
    <div className="bg-zinc-900 h-[562px] relative shrink-0 w-full" data-name="Section">
      <Heading1 />
      <Paragraph4 />
      <Button3 />
    </div>
  );
}

function Paragraph5() {
  return (
    <div className="h-[20px] relative shrink-0 w-[217.137px]" data-name="Paragraph">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid h-[20px] relative w-[217.137px]">
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[20px] left-0 text-[#52525c] text-[14px] text-nowrap top-[-1.2px] whitespace-pre">© 2025 ZIPFIT. All rights reserved.</p>
      </div>
    </div>
  );
}

function Text1() {
  return (
    <div className="bg-blue-50 h-[27.988px] relative rounded-[2.68435e+07px] shrink-0 w-[38.463px]" data-name="Text">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex h-[27.988px] items-start px-[12px] py-[6px] relative w-[38.463px]">
        <p className="font-['Arimo:Regular',sans-serif] font-normal leading-[16px] relative shrink-0 text-[#155dfc] text-[12px] text-nowrap whitespace-pre">LH</p>
      </div>
    </div>
  );
}

function Text2() {
  return (
    <div className="bg-green-50 h-[27.988px] relative rounded-[2.68435e+07px] shrink-0 w-[39.213px]" data-name="Text">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex h-[27.988px] items-start px-[12px] py-[6px] relative w-[39.213px]">
        <p className="font-['Arimo:Regular',sans-serif] font-normal leading-[16px] relative shrink-0 text-[#00a63e] text-[12px] text-nowrap whitespace-pre">SH</p>
      </div>
    </div>
  );
}

function Text3() {
  return (
    <div className="bg-purple-50 h-[27.988px] relative rounded-[2.68435e+07px] shrink-0 w-[41.125px]" data-name="Text">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex h-[27.988px] items-start px-[12px] py-[6px] relative w-[41.125px]">
        <p className="font-['Arimo:Regular',sans-serif] font-normal leading-[16px] relative shrink-0 text-[#9810fa] text-[12px] text-nowrap whitespace-pre">GH</p>
      </div>
    </div>
  );
}

function Container17() {
  return (
    <div className="h-[27.988px] relative shrink-0 w-[142.8px]" data-name="Container">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex gap-[12px] h-[27.988px] items-center relative w-[142.8px]">
        <Text1 />
        <Text2 />
        <Text3 />
      </div>
    </div>
  );
}

function Container18() {
  return (
    <div className="content-stretch flex h-[27.988px] items-center justify-between relative shrink-0 w-full" data-name="Container">
      <Paragraph5 />
      <Container17 />
    </div>
  );
}

function Footer() {
  return (
    <div className="bg-neutral-50 h-[124.787px] relative shrink-0 w-full" data-name="Footer">
      <div aria-hidden="true" className="absolute border-[0.8px_0px_0px] border-solid border-zinc-200 inset-0 pointer-events-none" />
      <div className="size-full">
        <div className="content-stretch flex flex-col h-[124.787px] items-start pb-0 pt-[48.8px] px-[16px] relative w-full">
          <Container18 />
        </div>
      </div>
    </div>
  );
}

export default function ZipfitLanding() {
  return (
    <div className="bg-white content-stretch flex flex-col gap-[66px] items-center relative size-full" data-name="zipfit_landing">
      <Section />
      <Section1 />
      <Section2 />
      <Footer />
    </div>
  );
}