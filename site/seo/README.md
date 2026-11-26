# 아임웹 SEO 설정에 넣은 코드 (설정 > SEO > 고급 설정)

## Header Code 상단
구글·네이버 소유확인 메타태그 (지우면 서치콘솔·서치어드바이저 인증이 풀림)

## Header Code
```html
<style>
/* PC 상단 */
.inline_widget.logo img.normal_logo{height:132px!important;width:auto!important;max-width:none!important}
.viewport-nav.desktop > li > a{padding-left:9px!important;padding-right:9px!important}
.viewport-nav.desktop > li:has(> a[href="/home"]){display:none!important}
/* 전후 갤러리 제목과 '시공 사례 더 보기' 글자 높이 맞춤 */
.cw-w03 .cw-head{align-items:baseline!important}
</style>
```

## Footer Code
```html
<script>
/* ' · ' 구분점이 줄 맨 앞에 오지 않게 앞 글자와 붙임 (모든 코드 위젯 공통) */
(function(){function fix(r){var w=document.createTreeWalker(r,NodeFilter.SHOW_TEXT,null),n;while(n=w.nextNode()){if(n.nodeValue.indexOf(' · ')>-1&&!n.parentNode.closest('style,script'))n.nodeValue=n.nodeValue.replace(/ · /g,' · ');}}function run(){var l=document.querySelectorAll('.cw');for(var i=0;i<l.length;i++)fix(l[i]);}if(document.readyState!=='loading')run();else document.addEventListener('DOMContentLoaded',run);})();
</script>
```

## 2026-11-26 로고 크기·정렬
- Header Code: PC 로고 높이 132px, 모바일 로고 너비 min(402px, 100vw-60px)·높이 auto, 모바일 로고 줄 116px, 스크롤 시 메뉴 고정 위치 top:116px
- Footer Code: 로고 위젯 왼쪽 여백을 JS로 조정해 로고 왼쪽 끝을 히어로 첫 줄(가정집…) 글자 위치(>900px: 70px, 561~900px: 38px, ≤560px: 30px)에 맞춤
