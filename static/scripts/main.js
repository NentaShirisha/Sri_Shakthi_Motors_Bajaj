const BODY_DATA = document.body.dataset || {};
const STATIC_PREFIX = window.__BAJAJ_STATIC_PREFIX || BODY_DATA.staticPrefix || '';
const STATIC_ROOT = STATIC_PREFIX && !STATIC_PREFIX.endsWith('/') ? `${STATIC_PREFIX}/` : STATIC_PREFIX;
const DATA_URL =
    window.__BAJAJ_DATA_URL ||
    BODY_DATA.dataUrl ||
    `${STATIC_ROOT}assets/data/bikes.json`;
const MODELS_ROOT = window.__BAJAJ_MODELS_ROOT || BODY_DATA.modelsRoot || 'models.html';
const DETAIL_PATTERN = window.__BAJAJ_DETAIL_PATTERN || BODY_DATA.detailPattern || '';
const BOOK_URL = window.__BAJAJ_BOOK_URL || BODY_DATA.bookUrl || 'book-test-ride.html';
const OFFERS_URL = window.__BAJAJ_OFFERS_URL || BODY_DATA.offersUrl || 'offers.html';
const PAGE_SLUG = BODY_DATA.bikeSlug || '';

function assetUrl(path = '') {
    if (!path) {
        return '';
    }
    if (/^(https?:)?\/\//.test(path) || path.startsWith('/')) {
        return path;
    }
    return `${STATIC_ROOT}${path}`;
}

function normalizeBike(bike) {
    if (!bike) {
        return null;
    }
    return {
        ...bike,
        heroImage: assetUrl(bike.heroImage),
        gallery: Array.isArray(bike.gallery) ? bike.gallery.map((item) => assetUrl(item)) : [],
    };
}

function detailUrl(slug) {
    if (!slug) {
        return MODELS_ROOT;
    }
    if (DETAIL_PATTERN && DETAIL_PATTERN.includes('__slug__')) {
        return DETAIL_PATTERN.replace('__slug__', slug);
    }
    const separator = MODELS_ROOT.endsWith('/') ? '' : '/';
    return `${MODELS_ROOT}${separator}${slug}/`;
}

const SELECTED_BIKE = normalizeBike(window.__BAJAJ_SELECTED_BIKE);

// Utility to fetch bike data once and cache it across pages.
const dataStore = {
    bikes: null,
    async loadBikes() {
        if (this.bikes) {
            return this.bikes;
        }
        const response = await fetch(DATA_URL);
        if (!response.ok) {
            throw new Error('Unable to load bike data');
        }
        const payload = await response.json();
        this.bikes = payload.bikes.map((bike) => normalizeBike(bike));
        return this.bikes;
    },
};

const pageInitializers = {
    home: async () => {
        initHeroSlider();
        initTestimonials();
        renderFeaturedBikes();
        renderOffersHighlight();
    },
    models: async () => {
        await renderModelsGrid();
        initFilters();
    },
    model: async () => {
        await renderModelDetail();
        initEmiCalculator();
    },
    offers: async () => {
        renderOffersHighlight();
    },
    book: async () => {
        await populateModelOptions('#testRideModel');
    },
    contact: async () => {
        await populateModelOptions('#contactModel', true);
    },
    service: async () => {
        await populateModelOptions('#serviceModel');
    },
};

function initNavHighlight() {
    const current = document.body.dataset.page;
    document.querySelectorAll('header nav a').forEach((link) => {
        if (link.dataset.page === current) {
            link.classList.add('active');
        }
    });
}

function initHeroSlider() {
    const slides = document.querySelectorAll('.hero-slide');
    if (!slides.length) {
        return;
    }
    let current = 0;
    slides[current].classList.add('active');
    setInterval(() => {
        slides[current].classList.remove('active');
        current = (current + 1) % slides.length;
        slides[current].classList.add('active');
    }, 5000);
}

function initTestimonials() {
    const testimonialContainer = document.querySelector('#testimonialCarousel');
    if (!testimonialContainer) {
        return;
    }
    const testimonials = [
        {
            quote: 'Sri Shakthi Motors Bajaj made my Pulsar delivery memorable. Quick finance approval and friendly team!',
            author: 'Anil Kumar',
            role: 'Pulsar N160 Owner',
        },
        {
            quote: 'Transparent pricing and hassle-free exchange. Highly recommend the Kadthal showroom.',
            author: 'Sravani M',
            role: 'Dominar 400 Rider',
        },
        {
            quote: 'Service reminders and pick-up facility are super helpful. They truly care after delivery too.',
            author: 'Venkatesh R',
            role: 'Avenger Cruise 220 Owner',
        },
    ];
    testimonialContainer.innerHTML = testimonials
        .map(
            (item) => `
                <article class="testimonial">
                    <p>“${item.quote}”</p>
                    <span class="author">${item.author}</span>
                    <span class="role">${item.role}</span>
                </article>
            `,
        )
        .join('');
}

async function renderFeaturedBikes() {
    const container = document.querySelector('#featuredBikes');
    if (!container) {
        return;
    }
    const bikes = await dataStore.loadBikes();
    const featured = bikes.filter((bike) => bike.isFeatured);
    container.innerHTML = featured
        .map((bike) => bikeCardTemplate(bike, true))
        .join('');
}

function renderOffersHighlight() {
    const banner = document.querySelector('#highlightBanner');
    if (!banner) {
        return;
    }
    const offers = [
        'Festive Freedom Offer: Save up to ₹12,000 on select Pulsar models',
        'Zero down payment with Bajaj Finance partners on Dominar and Avenger series',
        'Exchange bonus up to ₹10,000 for upgrading from any 2-wheeler',
    ];
    banner.innerHTML = `
        <h3>Ride Home Your Bajaj with Exclusive Kadthal Offers</h3>
        <p>${offers[0]}</p>
        <ul class="spec-list">
            ${offers.map((offer) => `<li>${offer}</li>`).join('')}
        </ul>
        <a class="btn btn-secondary" href="${BOOK_URL}">Grab the Offer</a>
    `;
}

async function renderModelsGrid() {
    const grid = document.querySelector('#modelsGrid');
    if (!grid) {
        return;
    }
    const bikes = await dataStore.loadBikes();
    grid.dataset.source = JSON.stringify(bikes);
    grid.innerHTML = bikes.map((bike) => bikeCardTemplate(bike)).join('');
}

function bikeCardTemplate(bike, compact = false) {
    const detailLink = detailUrl(bike.slug);
    const bookButton = compact ? '' : `<a class="btn btn-secondary" href="${BOOK_URL}">Book Test Ride</a>`;
    return `
        <article class="card model-card" data-slug="${bike.slug}" data-family="${bike.family}" data-price="${bike.price.exShowroom}">
            <span class="tag">${bike.family}</span>
            <img src="${bike.heroImage}" alt="${bike.name} - hero image" loading="lazy">
            <h3>${bike.name}</h3>
            ${bike.performance && bike.performance.summary ? `<p class="summary">${bike.performance.summary}</p>` : ''}
            <p class="price">₹${bike.price.exShowroom.toLocaleString()} onwards</p>
            <ul class="spec-list">
                <li><strong>Engine:</strong> ${bike.engine.cc}cc | ${bike.engine.power}</li>
                <li><strong>Mileage:</strong> ${bike.performance.mileage}</li>
                <li><strong>Colors:</strong> ${bike.colors.join(', ')}</li>
            </ul>
            <div class="hero-actions">
                <a class="btn btn-primary" href="${detailLink}">View Details</a>
                ${bookButton}
            </div>
        </article>
    `;
}

function initFilters() {
    const filterForm = document.querySelector('#filterForm');
    const grid = document.querySelector('#modelsGrid');
    if (!filterForm || !grid) {
        return;
    }
    filterForm.addEventListener('input', () => {
        const bikes = JSON.parse(grid.dataset.source || '[]');
        const family = filterForm.querySelector('#filterFamily').value;
        const maxPrice = filterForm.querySelector('#filterPrice').value;
        const engine = filterForm.querySelector('#filterEngine').value;
        const filtered = bikes.filter((bike) => {
            const matchesFamily = !family || bike.family === family;
            const matchesPrice = !maxPrice || bike.price.exShowroom <= Number(maxPrice);
            const matchesEngine = !engine || bike.engine.ccCategory === engine;
            return matchesFamily && matchesPrice && matchesEngine;
        });
        grid.innerHTML = filtered.length
            ? filtered.map((bike) => bikeCardTemplate(bike)).join('')
            : '<p>No bikes match your selection. Try adjusting the filters.</p>';
    });
}

async function renderModelDetail() {
    const detailWrap = document.querySelector('#modelDetail');
    if (!detailWrap) {
        return;
    }
    const slug = PAGE_SLUG || new URLSearchParams(window.location.search).get('bike');
    if (!slug) {
        detailWrap.innerHTML = `<p>Bike not found. Please select a model from the <a class="btn" href="${MODELS_ROOT}">catalog</a>.</p>`;
        return;
    }
    let bike = SELECTED_BIKE && SELECTED_BIKE.slug === slug ? SELECTED_BIKE : null;
    if (!bike) {
        const bikes = await dataStore.loadBikes();
        bike = bikes.find((item) => item.slug === slug) || null;
    }
    if (!bike) {
        detailWrap.innerHTML = `<p>Bike not found. Please choose a different model from the <a class="btn" href="${MODELS_ROOT}">catalog</a>.</p>`;
        return;
    }
    document.title = `${bike.name} | Sri Shakthi Motors Bajaj`;
    detailWrap.innerHTML = `
        <div class="card" style="display: grid; gap: 1rem;">
            <span class="tag">${bike.family}</span>
            <h1 style="font-family: var(--font-heading);">${bike.name}</h1>
            <p>${bike.performance.summary || 'Engineered for power, control, and everyday excitement.'}</p>
            <div class="badge-group">
                <span class="badge">${bike.engine.power}</span>
                <span class="badge">${bike.performance.mileage} mileage</span>
                <span class="badge">${bike.engine.transmission}</span>
            </div>
            <div>
                <strong>Starting at:</strong>
                <div class="price">₹${bike.price.exShowroom.toLocaleString()} ex-showroom</div>
            </div>
            <div class="hero-actions">
                <a class="btn btn-primary" href="${BOOK_URL}">Book Test Ride</a>
                <a class="btn btn-secondary" href="${OFFERS_URL}">View Offers</a>
            </div>
        </div>
        <div class="card">
            <img src="${bike.heroImage}" alt="${bike.name}" style="border-radius: 12px;">
        </div>
    `;
    renderGallery(bike.gallery);
    renderSpecifications(bike);
    renderPricing(bike.price);
    await populateModelOptions('#testRideInline', false, bike.slug);
}

function renderGallery(images = []) {
    const container = document.querySelector('#modelGallery');
    if (!container) {
        return;
    }
    if (!images.length) {
        container.innerHTML = '<p>Gallery coming soon.</p>';
        return;
    }
    container.innerHTML = images
        .map((src) => `<img src="${src}" alt="Bajaj bike angle" loading="lazy">`)
        .join('');
}

function renderSpecifications(bike) {
    const specsContainer = document.querySelector('#specifications');
    if (!specsContainer) {
        return;
    }
    specsContainer.innerHTML = `
        <section class="spec-block">
            <h4>Engine & Performance</h4>
            <ul class="spec-list">
                <li>Displacement: ${bike.engine.cc}cc</li>
                <li>Power: ${bike.engine.power}</li>
                <li>Torque: ${bike.engine.torque}</li>
                <li>Cooling: ${bike.engine.cooling}</li>
                <li>Transmission: ${bike.engine.transmission}</li>
            </ul>
        </section>
        <section class="spec-block">
            <h4>Chassis & Brakes</h4>
            <ul class="spec-list">
                <li>Front Brake: ${bike.chassis.frontBrake}</li>
                <li>Rear Brake: ${bike.chassis.rearBrake}</li>
                <li>Suspension: ${bike.chassis.suspension}</li>
                <li>Kerb Weight: ${bike.chassis.weight}</li>
                <li>Seat Height: ${bike.chassis.seatHeight}</li>
            </ul>
        </section>
        <section class="spec-block">
            <h4>Technology & Features</h4>
            <ul class="spec-list">
                ${bike.features.map((feature) => `<li>${feature}</li>`).join('')}
            </ul>
        </section>
    `;
    const colorList = document.querySelector('#colorOptions');
    if (colorList) {
        colorList.innerHTML = bike.colors.map((color) => `<span class="badge">${color}</span>`).join('');
    }
}

function renderPricing(price) {
    const tableWrap = document.querySelector('#priceBreakdown');
    if (!tableWrap) {
        return;
    }
    tableWrap.innerHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Price Component</th>
                    <th>Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Ex-Showroom (Kadthal)</td>
                    <td>${price.exShowroom.toLocaleString()}</td>
                </tr>
                <tr>
                    <td>On-Road (Approx.)</td>
                    <td>${price.onRoad.toLocaleString()}</td>
                </tr>
                <tr>
                    <td>EMI Starting</td>
                    <td>${price.emi}</td>
                </tr>
            </tbody>
        </table>
    `;
}

async function populateModelOptions(selector, includePlaceholder = false, preselectSlug) {
    const select = document.querySelector(selector);
    if (!select) {
        return;
    }
    try {
        const bikes = await dataStore.loadBikes();
        if (bikes && bikes.length > 0) {
            const options = bikes
                .map((bike) => `<option value="${bike.slug}" ${preselectSlug === bike.slug ? 'selected' : ''}>${bike.name}</option>`)
                .join('');
            select.innerHTML = includePlaceholder
                ? `<option value="">Select Bike Model</option>${options}`
                : options;
        }
    } catch (error) {
        console.warn('Failed to load bikes for dropdown:', error);
        // Keep server-side options if fetch fails
    }
}

function initEmiCalculator() {
    const form = document.querySelector('#emiForm');
    const resultField = document.querySelector('#emiResult');
    if (!form || !resultField) {
        return;
    }
    form.addEventListener('input', () => {
        const principal = Number(form.querySelector('#loanAmount').value || 0);
        const rate = Number(form.querySelector('#interestRate').value || 0) / 1200;
        const months = Number(form.querySelector('#loanTenure').value || 0) * 12;
        if (!principal || !rate || !months) {
            resultField.textContent = '—';
            return;
        }
        const factor = Math.pow(1 + rate, months);
        const emi = (principal * rate * factor) / (factor - 1);
        resultField.textContent = `₹${emi.toFixed(0).toLocaleString()}`;
    });
}

function initWhatsAppButton() {
    const button = document.querySelector('#whatsappButton');
    if (!button) {
        return;
    }
    button.addEventListener('click', () => {
        const phone = button.dataset.phone;
    const message = encodeURIComponent('Hi Sri Shakthi Motors Bajaj, I would like to know more about the latest offers.');
        window.open(`https://wa.me/${phone}?text=${message}`, '_blank');
    });
}

window.addEventListener('DOMContentLoaded', async () => {
    initNavHighlight();
    const page = document.body.dataset.page;
    if (pageInitializers[page]) {
        try {
            await pageInitializers[page]();
        } catch (error) {
            console.error(error);
        }
    }
    initWhatsAppButton();
});
