<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>카카오맵 주소 · 좌표 · 위성지도 · 로드뷰 검색기</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background-color: #f4f6f9; }
        
        /* 상단 헤더 */
        header {
            background-color: #ffffff;
            padding: 12px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 10;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            justify-content: space-between;
        }
        .title-area h1 { font-size: 17px; color: #1e293b; font-weight: 700; }
        .title-area p { font-size: 12px; color: #64748b; margin-top: 2px; }

        .search-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }
        .input-group {
            display: flex;
            align-items: center;
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            overflow: hidden;
        }
        .input-group label {
            padding: 0 10px;
            font-size: 12px;
            font-weight: bold;
            color: #334155;
            background: #e2e8f0;
            height: 34px;
            display: flex;
            align-items: center;
        }
        .input-group input {
            border: none;
            background: transparent;
            padding: 0 10px;
            height: 34px;
            font-size: 13px;
            outline: none;
            width: 190px;
        }
        .input-group button {
            height: 34px;
            padding: 0 12px;
            border: none;
            background-color: #2563eb;
            color: white;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        .input-group button:hover { background-color: #1d4ed8; }

        /* 툴바 그룹 (지도타입 / 뷰분할 / 로드뷰도로선) */
        .toolbar-group {
            display: flex;
            gap: 4px;
            background: #f1f5f9;
            padding: 3px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
        }
        .tool-btn {
            border: none;
            background: transparent;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: bold;
            color: #475569;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .tool-btn.active {
            background: #ffffff;
            color: #2563eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .road-layer-btn {
            border: 1px solid #94a3b8;
            background: #ffffff;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: bold;
            color: #334155;
            border-radius: 6px;
            cursor: pointer;
        }
        .road-layer-btn.active {
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
        }

        /* 메인 영역 (지도 + 로드뷰 + 정보 패널) */
        .main-container {
            display: flex;
            flex: 1;
            position: relative;
            overflow: hidden;
        }
        .visual-area {
            display: flex;
            flex: 1;
            height: 100%;
            position: relative;
        }
        #map-wrapper, #rv-wrapper {
            flex: 1;
            height: 100%;
            position: relative;
            transition: all 0.2s ease;
        }
        #rv-wrapper {
            border-left: 2px solid #cbd5e1;
            background-color: #1e293b;
        }
        #map, #roadview {
            width: 100%;
            height: 100%;
        }

        /* 뷰 모드 상태 클래스 */
        .visual-area.mode-map #rv-wrapper { display: none; }
        .visual-area.mode-roadview #map-wrapper { display: none; }
        .visual-area.mode-roadview #rv-wrapper { border-left: none; }

        /* 로드뷰 없음 안내 오버레이 */
        #rv-empty {
            position: absolute;
            inset: 0;
            background: rgba(15, 23, 42, 0.85);
            color: #f8fafc;
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            z-index: 5;
        }
        #rv-empty p { font-size: 14px; margin-bottom: 6px; font-weight: bold; }
        #rv-empty span { font-size: 12px; color: #94a3b8; }

        /* 에러 안내 박스 */
        .error-box {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            border: 1px solid #fca5a5;
            border-left: 5px solid #ef4444;
            border-radius: 8px;
            padding: 24px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            line-height: 1.6;
            color: #1e293b;
            z-index: 20;
        }
        .error-box h3 { color: #dc2626; margin-bottom: 10px; font-size: 16px; }
        .error-box ul { margin-left: 20px; font-size: 13px; color: #475569; }
        .error-box li { margin-bottom: 6px; }
        .error-box code { background: #f1f5f9; padding: 2px 5px; border-radius: 4px; color: #0f172a; }

        /* 우측 결과 정보 패널 */
        .info-panel {
            width: 310px;
            background: #ffffff;
            border-left: 1px solid #e2e8f0;
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            overflow-y: auto;
            box-shadow: -2px 0 8px rgba(0,0,0,0.05);
        }
        .info-panel h2 {
            font-size: 15px;
            color: #0f172a;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 8px;
        }
        .info-item {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px 12px;
        }
        .info-item .label {
            font-size: 12px;
            color: #64748b;
            font-weight: bold;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .info-item .value {
            font-size: 13px;
            color: #1e293b;
            word-break: break-all;
            line-height: 1.4;
            min-height: 18px;
        }
        .copy-btn {
            background: #e2e8f0;
            border: none;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            color: #334155;
            cursor: pointer;
            font-weight: bold;
        }
        .copy-btn:hover { background: #cbd5e1; }

        .rv-status-badge {
            font-size: 12px;
            padding: 8px 10px;
            border-radius: 6px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            color: #1e40af;
            line-height: 1.4;
        }

        /* 토스트 알림 */
        #toast {
            visibility: hidden;
            min-width: 220px;
            background-color: #1e293b;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px 16px;
            position: fixed;
            z-index: 100;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        #toast.show { visibility: visible; animation: fadein 0.3s, fadeout 0.3s 1.7s; }
        @keyframes fadein { from {bottom: 10px; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 10px; opacity: 0;} }
    </style>
</head>
<body>

<header>
    <div class="title-area">
        <h1>📍 카카오맵 주소 · 좌표 · 위성 · 로드뷰</h1>
        <p>일반/위성지도 전환 및 클릭·검색 위치의 로드뷰를 실시간으로 확인합니다.</p>
    </div>

    <div class="search-controls">
        <div class="input-group">
            <label for="addressInput">주소/장소</label>
            <input type="text" id="addressInput" placeholder="예: 서울시청 또는 세종대로 110" onkeypress="if(event.key==='Enter') searchByAddress()">
            <button onclick="searchByAddress()">검색</button>
        </div>

        <div class="input-group">
            <label for="coordInput">좌표</label>
            <input type="text" id="coordInput" placeholder="예: 37.5665, 126.9780" onkeypress="if(event.key==='Enter') searchByCoord()">
            <button onclick="searchByCoord()">이동</button>
        </div>

        <!-- 일반지도 / 위성지도 전환 -->
        <div class="toolbar-group" title="지도 배경 스타일 전환">
            <button class="tool-btn active" id="type-roadmap" onclick="setMapType('roadmap')">🗺️ 일반지도</button>
            <button class="tool-btn" id="type-skyview" onclick="setMapType('skyview')">🛰️ 위성지도</button>
        </div>

        <!-- 로드뷰 도로선 오버레이 -->
        <button id="roadLayerBtn" class="road-layer-btn active" onclick="toggleRoadviewLayer()" title="지도에 로드뷰 촬영 도로 표시">
            🛣️ 로드뷰선 ON
        </button>

        <!-- 화면 분할 모드 -->
        <div class="toolbar-group" title="화면 분할 모드 선택">
            <button class="tool-btn active" id="btn-split" onclick="setViewMode('split')">지도+로드뷰</button>
            <button class="tool-btn" id="btn-map" onclick="setViewMode('map')">지도만</button>
            <button class="tool-btn" id="btn-rv" onclick="setViewMode('roadview')">로드뷰만</button>
        </div>
    </div>
</header>

<div class="main-container">
    <div class="visual-area mode-split" id="visualArea">
        <div id="map-wrapper">
            <div id="map"></div>
        </div>
        <div id="rv-wrapper">
            <div id="roadview"></div>
            <div id="rv-empty">
                <p>🚫 반경 50m 이내에 로드뷰 데이터가 없습니다</p>
                <span>파란색 로드뷰 도로선 근처를 클릭해 보세요.</span>
            </div>
        </div>
    </div>
    
    <aside class="info-panel">
        <h2>선택 위치 상세 정보</h2>
        
        <div class="info-item">
            <div class="label">
                <span>도로명 주소</span>
                <button class="copy-btn" onclick="copyText('roadAddr')">복사</button>
            </div>
            <div class="value" id="roadAddr">-</div>
        </div>

        <div class="info-item">
            <div class="label">
                <span>지번 주소</span>
                <button class="copy-btn" onclick="copyText('jibunAddr')">복사</button>
            </div>
            <div class="value" id="jibunAddr">-</div>
        </div>

        <div class="info-item">
            <div class="label">
                <span>위도 (Latitude / Y)</span>
                <button class="copy-btn" onclick="copyText('latVal')">복사</button>
            </div>
            <div class="value" id="latVal">-</div>
        </div>

        <div class="info-item">
            <div class="label">
                <span>경도 (Longitude / X)</span>
                <button class="copy-btn" onclick="copyText('lngVal')">복사</button>
            </div>
            <div class="value" id="lngVal">-</div>
        </div>

        <div class="info-item">
            <div class="label">
                <span>위도, 경도 (통합)</span>
                <button class="copy-btn" onclick="copyText('latLngCombined')">복사</button>
            </div>
            <div class="value" id="latLngCombined">-</div>
        </div>

        <div class="rv-status-badge" id="rvInfoBadge">
            📸 로드뷰 상태: 확인 중...
        </div>
    </aside>
</div>

<div id="toast">클립보드에 복사되었습니다.</div>

<!-- 반드시 YOUR_KAKAO_JAVASCRIPT_KEY를 실제 JavaScript 키로 변경하세요 -->
<script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=a8ab0c24096e177ce69d0862bbaa9f54&libraries=services&autoload=false"></script>

<script>
    let map, geocoder, ps, marker, infowindow;
    let roadview, roadviewClient, rvMarker;
    let isRoadLayerOn = true;

    window.addEventListener('DOMContentLoaded', function() {
        const mapContainer = document.getElementById('map');

        if (typeof kakao === 'undefined' || !kakao.maps) {
            document.getElementById('visualArea').innerHTML = `
                <div class="error-box">
                    <h3>⚠️ 카카오맵 SDK를 불러오지 못했습니다</h3>
                    <ul>
                        <li><strong>1. 실행 경로 확인:</strong> 현재 주소가 <code>${window.location.origin}</code> 입니다. 로컬 웹 서버(<code>python -m http.server 8000</code>)로 실행하세요.</li>
                        <li><strong>2. 도메인 등록:</strong> Kakao Developers &gt; [플랫폼] &gt; [Web]에 <code>${window.location.origin}</code>을 등록하세요.</li>
                        <li><strong>3. API 키 및 활성화:</strong> <strong>JavaScript 키</strong> 입력 및 [카카오맵] 활성화 <strong>ON</strong> 여부를 확인하세요.</li>
                    </ul>
                </div>`;
            return;
        }

        kakao.maps.load(function() {
            const defaultPos = new kakao.maps.LatLng(37.566826, 126.9786567);

            // 1. 지도 초기화
            map = new kakao.maps.Map(mapContainer, {
                center: defaultPos,
                level: 3
            });

            // 줌 컨트롤 추가 (우측 상단)
            const zoomControl = new kakao.maps.ZoomControl();
            map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

            // 기본으로 로드뷰 도로망(파란색 선) 오버레이 활성화
            map.addOverlayMapTypeId(kakao.maps.MapTypeId.ROADVIEW);

            geocoder = new kakao.maps.services.Geocoder();
            ps = new kakao.maps.services.Places();

            marker = new kakao.maps.Marker({ position: defaultPos, map: map });
            infowindow = new kakao.maps.InfoWindow({ zIndex: 1 });

            // 2. 로드뷰 초기화
            const rvContainer = document.getElementById('roadview');
            roadview = new kakao.maps.Roadview(rvContainer);
            roadviewClient = new kakao.maps.RoadviewClient();

            const rvIcon = new kakao.maps.MarkerImage(
                'https://t1.daumcdn.net/localimg/localimages/07/2018/pc/roadview_minimap_wk_2018.png',
                new kakao.maps.Size(26, 46),
                {
                    spriteSize: new kakao.maps.Size(1666, 168),
                    spriteOrigin: new kakao.maps.Point(705, 114),
                    offset: new kakao.maps.Point(13, 46)
                }
            );
            rvMarker = new kakao.maps.Marker({
                image: rvIcon,
                position: defaultPos,
                map: map
            });

            kakao.maps.event.addListener(roadview, 'position_changed', function() {
                const rvPosition = roadview.getPosition();
                rvMarker.setPosition(rvPosition);
                map.setCenter(rvPosition);
            });

            updateLocationByCoords(defaultPos);

            kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
                updateLocationByCoords(mouseEvent.latLng);
            });
        });
    });

    // 일반지도 / 위성지도(하이브리드) 전환
    function setMapType(maptype) {
        if (!map) return;
        const roadmapBtn = document.getElementById('type-roadmap');
        const skyviewBtn = document.getElementById('type-skyview');

        if (maptype === 'roadmap') {
            map.setMapTypeId(kakao.maps.MapTypeId.ROADMAP);
            roadmapBtn.classList.add('active');
            skyviewBtn.classList.remove('active');
        } else {
            // HYBRID는 위성영상 위에 도로명/건물명 라벨을 함께 표시하여 위치 판별에 유리
            map.setMapTypeId(kakao.maps.MapTypeId.HYBRID);
            skyviewBtn.classList.add('active');
            roadmapBtn.classList.remove('active');
        }
    }

    // 화면 분할 모드 전환
    function setViewMode(mode) {
        const visualArea = document.getElementById('visualArea');
        visualArea.className = `visual-area mode-${mode}`;

        document.getElementById('btn-split').classList.toggle('active', mode === 'split');
        document.getElementById('btn-map').classList.toggle('active', mode === 'map');
        document.getElementById('btn-rv').classList.toggle('active', mode === 'roadview');

        setTimeout(() => {
            if (map) map.relayout();
            if (roadview) roadview.relayout();
            if (marker && map) map.setCenter(marker.getPosition());
        }, 220);
    }

    // 지도 위 파란색 로드뷰 도로선 ON/OFF
    function toggleRoadviewLayer() {
        if (!map) return;
        const btn = document.getElementById('roadLayerBtn');
        if (isRoadLayerOn) {
            map.removeOverlayMapTypeId(kakao.maps.MapTypeId.ROADVIEW);
            btn.classList.remove('active');
            btn.innerText = '🛣️ 로드뷰선 OFF';
        } else {
            map.addOverlayMapTypeId(kakao.maps.MapTypeId.ROADVIEW);
            btn.classList.add('active');
            btn.innerText = '🛣️ 로드뷰선 ON';
        }
        isRoadLayerOn = !isRoadLayerOn;
    }

    // 주소/장소 검색
    function searchByAddress() {
        if (!geocoder) return alert('지도가 아직 초기화되지 않았습니다.');
        const query = document.getElementById('addressInput').value.trim();
        if (!query) return alert('검색할 주소나 장소명을 입력하세요.');

        geocoder.addressSearch(query, function(result, status) {
            if (status === kakao.maps.services.Status.OK) {
                const coords = new kakao.maps.LatLng(result[0].y, result[0].x);
                map.setCenter(coords);
                updateLocationByCoords(coords);
            } else {
                ps.keywordSearch(query, function(data, status) {
                    if (status === kakao.maps.services.Status.OK) {
                        const coords = new kakao.maps.LatLng(data[0].y, data[0].x);
                        map.setCenter(coords);
                        updateLocationByCoords(coords, data[0].place_name);
                    } else {
                        alert('검색 결과가 없습니다. 정확한 주소나 장소명을 입력해주세요.');
                    }
                });
            }
        });
    }

    // 좌표 검색
    function searchByCoord() {
        if (!geocoder) return alert('지도가 아직 초기화되지 않았습니다.');
        const input = document.getElementById('coordInput').value.trim();
        if (!input) return alert('좌표를 입력하세요. (예: 37.5665, 126.9780)');

        const parts = input.split(/[\s,]+/).filter(Boolean);
        if (parts.length !== 2 || isNaN(parts[0]) || isNaN(parts[1])) {
            return alert('올바른 좌표 형식이 아닙니다.\n"위도, 경도" 형식으로 입력해주세요.');
        }

        let lat = parseFloat(parts[0]);
        let lng = parseFloat(parts[1]);

        if (lat > 100 && lng < 50) {
            [lat, lng] = [lng, lat];
            showToast('경도·위도 순서가 자동 보정되었습니다.');
        }

        const coords = new kakao.maps.LatLng(lat, lng);
        map.setCenter(coords);
        updateLocationByCoords(coords);
    }

    // 좌표 기반 주소 변환 + 로드뷰 업데이트
    function updateLocationByCoords(latlng, placeName = '') {
        const lat = latlng.getLat().toFixed(7);
        const lng = latlng.getLng().toFixed(7);

        marker.setPosition(latlng);

        document.getElementById('latVal').innerText = lat;
        document.getElementById('lngVal').innerText = lng;
        document.getElementById('latLngCombined').innerText = `${lat}, ${lng}`;

        geocoder.coord2Address(latlng.getLng(), latlng.getLat(), function(result, status) {
            let roadAddr = '도로명 주소 없음';
            let jibunAddr = '지번 주소 없음';

            if (status === kakao.maps.services.Status.OK) {
                if (result[0].road_address) {
                    roadAddr = result[0].road_address.address_name;
                    if (result[0].road_address.building_name) {
                        roadAddr += ` (${result[0].road_address.building_name})`;
                    }
                }
                if (result[0].address) {
                    jibunAddr = result[0].address.address_name;
                }
            }

            document.getElementById('roadAddr').innerText = roadAddr;
            document.getElementById('jibunAddr').innerText = jibunAddr;

            const titleHtml = placeName ? `<strong>${placeName}</strong><br>` : '';
            const displayAddr = (roadAddr !== '도로명 주소 없음') ? roadAddr : jibunAddr;
            const iwContent = `
                <div style="padding:8px 12px; font-size:12px; line-height:1.5; max-width:250px;">
                    ${titleHtml}
                    <span style="color:#1e293b;">${displayAddr}</span><br>
                    <span style="color:#2563eb; font-weight:bold;">${lat}, ${lng}</span>
                </div>`;
            infowindow.setContent(iwContent);
            infowindow.open(map, marker);
        });

        const rvEmptyEl = document.getElementById('rv-empty');
        const rvBadgeEl = document.getElementById('rvInfoBadge');

        roadviewClient.getNearestPanoId(latlng, 50, function(panoId) {
            if (panoId === null) {
                rvEmptyEl.style.display = 'flex';
                rvMarker.setMap(null);
                rvBadgeEl.innerText = '📸 로드뷰: 반경 50m 내 촬영 데이터 없음';
            } else {
                rvEmptyEl.style.display = 'none';
                rvMarker.setMap(map);
                roadview.setPanoId(panoId, latlng);
                rvBadgeEl.innerText = '📸 로드뷰: 정상 연동됨 (화면 드래그로 회전 가능)';
            }
        });
    }

    function copyText(elementId) {
        const text = document.getElementById(elementId).innerText;
        if (!text || text === '-' || text.includes('없음')) {
            return showToast('복사할 내용이 없습니다.');
        }

        navigator.clipboard.writeText(text).then(() => {
            showToast(`복사됨: ${text}`);
        }).catch(() => {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast(`복사됨: ${text}`);
        });
    }

    function showToast(message) {
        const toast = document.getElementById('toast');
        toast.innerText = message;
        toast.className = 'show';
        setTimeout(() => { toast.className = toast.className.replace('show', ''); }, 2000);
    }
</script>

</body>
</html>
