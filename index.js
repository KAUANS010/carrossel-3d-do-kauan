// ==========================================
// CONFIGURAÇÕES GLOBAIS
// ==========================================
const CONFIG = {
    baseItemSize: 80,      // Tamanho do ícone/imagem em pixels
    spacingRatio: 0.3,      // Espaçamento de profundidade
    maxSpeed: 1.5,          // Velocidade máxima do mouse
    easeFactor: 0.05,       // Suavização da busca
    ellipseWidthFactor: 0.4 // Define a largura da elipse baseada na tela (0.4 = 80% da tela)
};

let currentRotation = 0;
let targetSpeed = 0;
let radiusZ = 0;
let radiusX = 0;
let totalItems = 0;
let itemsData = [];
let itemsElements = []; // Guarda as tags HTML <a> para animá-las no loop
let carouselMode = 'mouse';
let searchTargetRotation = 0;
let isPaused = false; // Controla se o giro pelo mouse está pausado

async function initCarousel() {
    try {
        const response = await fetch('dados.json');
        if (!response.ok) throw new Error(`Erro: ${response.status}`);

        itemsData = await response.json();
        const carousel = document.getElementById('carousel');
        const datalist = document.getElementById('carousel-options');

        totalItems = itemsData.length;

        // Profundidade da elipse
        const spacing = CONFIG.baseItemSize * CONFIG.spacingRatio;
        radiusZ = Math.round((CONFIG.baseItemSize / 2) / Math.tan(Math.PI / totalItems)) + spacing;

        // Injeta variáveis CSS base
        const root = document.documentElement;
        root.style.setProperty('--item-size', `${CONFIG.baseItemSize}px`);
        root.style.setProperty('--translate-z', `${-radiusZ}px`);
        root.style.setProperty('--perspective', `${Math.max(1200, radiusZ * 3)}px`);

        // Renderiza itens e preenche o Datalist
        itemsData.forEach((item) => {
            // Criação do item 3D
            const anchor = document.createElement('a');
            anchor.href = item.href;
            anchor.target = "_blank";
            anchor.rel = "noopener noreferrer";
            anchor.className = 'carousel-item';
            anchor.title = item.alt;

            const img = document.createElement('img');
            img.src = item.img;
            img.alt = item.alt;
            img.loading = "lazy";

            anchor.appendChild(img);
            carousel.appendChild(anchor);
            itemsElements.push(anchor);

            // Criação da opção no menu suspenso
            const option = document.createElement('option');
            option.value = item.alt;
            datalist.appendChild(option);
        });

        updateDimensions();
        window.addEventListener('resize', updateDimensions);

        setupMouseControl();
        setupSearchControl();
        setupGlobalShortcuts();
        animateCarousel();
        document.getElementById("searchInput").focus();
    } catch (error) {
        console.error("Erro na inicialização:", error);
    }
}

// Atualiza a largura da elipse quando a tela mudar de tamanho
function updateDimensions() {
    radiusX = window.innerWidth * CONFIG.ellipseWidthFactor;
}

function focusAndSelectSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.focus();
        searchInput.select();
    }
}

function setupMouseControl() {
    window.addEventListener('mousemove', (event) => {
        if (carouselMode === 'search' || isPaused) return;

        const screenWidth = window.innerWidth;
        const mouseX = event.clientX;
        const position = (mouseX / screenWidth) * 2 - 1;

        if (Math.abs(position) < 0.1) {
            targetSpeed = 0;
        } else {
            targetSpeed = position * CONFIG.maxSpeed;
        }
    });

    document.addEventListener('mouseleave', () => {
        if (carouselMode === 'mouse') targetSpeed = 0;
    });

    document.addEventListener('click', (event) => {
        const clickedOnItem = event.target.closest('.carousel-item');
        const clickedOnHeader = event.target.closest('.search-header');

        if (!clickedOnItem && !clickedOnHeader) {
            isPaused = !isPaused;
            if (isPaused) {
                targetSpeed = 0;
            }
        }
    });

    document.addEventListener('dblclick', (event) => {
        const clickedOnItem = event.target.closest('.carousel-item');
        const clickedOnHeader = event.target.closest('.search-header');

        if (!clickedOnItem && !clickedOnHeader) {
            isPaused = false;
            focusAndSelectSearch();
        }
    });
}

function setupSearchControl() {
    const searchInput = document.getElementById('searchInput');

    searchInput.addEventListener('focus', (e) => {
        e.target.select();
    });

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();

        if (query === '') {
            carouselMode = 'mouse';
            searchInput.style.borderColor = '';
            return;
        }

        const matchIndex = itemsData.findIndex(item =>
            item.alt.toLowerCase().includes(query) ||
            item.alt.toLowerCase().split(' ').some(word => word.startsWith(query))
        );

        if (matchIndex !== -1) {
            carouselMode = 'search';
            isPaused = false;
            const itemAngle = matchIndex * (360 / totalItems);
            const target = -itemAngle;

            let diff = (target - currentRotation) % 360;
            if (diff > 180) diff -= 360;
            if (diff < -180) diff += 360;

            searchTargetRotation = currentRotation + diff;

            searchInput.style.borderColor = '#4CAF50';
            searchInput.style.borderWidth = '2px';
            searchInput.style.borderStyle = 'solid';
        } else {
            searchInput.style.borderColor = '#ff4444';
            searchInput.style.borderWidth = '2px';
            searchInput.style.borderStyle = 'solid';
        }
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.toLowerCase().trim();

            const matchItem = itemsData.find(item =>
                item.alt.toLowerCase().includes(query) ||
                item.alt.toLowerCase().split(' ').some(word => word.startsWith(query))
            );

            if (matchItem) {
                window.open(matchItem.href, '_blank');
                searchInput.value = '';
                searchInput.style.borderColor = '';
                carouselMode = 'mouse';
            } else {
                searchInput.style.borderColor = '#ff4444';
                searchInput.style.borderWidth = '2px';
                searchInput.style.borderStyle = 'solid';

                setTimeout(() => {
                    searchInput.style.borderColor = '';
                }, 3000);
            }
        }
    });

    searchInput.addEventListener('blur', () => {
        if (searchInput.value === '') {
            searchInput.style.borderColor = '';
        }
    });
}

function setupGlobalShortcuts() {
    window.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            isPaused = false;
            focusAndSelectSearch();
        }
    });
}

function animateCarousel() {
    if (carouselMode === 'mouse') {
        if (!isPaused) {
            currentRotation += targetSpeed;
        }
    } else if (carouselMode === 'search') {
        currentRotation += (searchTargetRotation - currentRotation) * CONFIG.easeFactor;
    }

    itemsElements.forEach((el, index) => {
        const baseAngle = index * (360 / totalItems);
        const currentItemAngle = baseAngle + currentRotation;
        const rad = currentItemAngle * (Math.PI / 180);

        const x = radiusX * Math.sin(rad);
        const z = radiusZ * Math.cos(rad);

        el.style.transform = `translateX(${x}px) translateZ(${z}px) rotateY(${currentItemAngle}deg)`;
    });

    requestAnimationFrame(animateCarousel);
}

document.addEventListener('DOMContentLoaded', initCarousel);