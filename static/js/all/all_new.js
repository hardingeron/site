(function () {
  const state = {
    page: 1,
    perPage: 15,
    destinationCity: 'all',
    originCity: 'all',
    range: '',
    loading: false,
    hasMore: false,
    items: new Map(),
  };

  const els = {
    list: document.getElementById('parcelList'),
    loadMore: document.getElementById('loadMore'),
    resultTitle: document.getElementById('resultTitle'),
    resultMeta: document.getElementById('resultMeta'),
    customDates: document.getElementById('customDates'),
    toastStack: document.getElementById('toastStack'),
    lightbox: document.getElementById('imageLightbox'),
    lightboxImage: document.getElementById('lightboxImage'),
    lightboxCaption: document.getElementById('lightboxCaption'),
    editOverlay: document.getElementById('editOverlay'),
    editForm: document.getElementById('editForm'),
    addOverlay: document.getElementById('addOverlay'),
    addFrame: document.getElementById('addParcelFrame'),
    addCloseChoice: document.getElementById('addCloseChoice'),
  };

  let addCloseResolve = null;

  const filterIds = [
    'filterSearch',
    'filterPayment',
    'filterStatus',
    'filterSender',
    'filterSenderPhone',
    'filterRecipient',
    'filterRecipientPhone',
    'filterDateFrom',
    'filterDateTo',
  ];

  const metrics = {
    total: document.getElementById('metricTotal'),
    active: document.getElementById('metricActive'),
    issued: document.getElementById('metricIssued'),
    weight: document.getElementById('metricWeight'),
    profitGel: document.getElementById('metricProfitGel'),
    profitRub: document.getElementById('metricProfitRub'),
    dueGel: document.getElementById('metricDueGel'),
    dueRub: document.getElementById('metricDueRub'),
    moscow: document.getElementById('metricMoscow'),
    spb: document.getElementById('metricSpb'),
    tbilisi: document.getElementById('metricTbilisi'),
    batumi: document.getElementById('metricBatumi'),
  };

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function formatNumber(value) {
    return new Intl.NumberFormat('ka-GE', { maximumFractionDigits: 2 }).format(Number(value || 0));
  }

  function cityLabel(value) {
    const city = String(value || '').trim();
    if (city === 'Moscow') return 'მოსკოვი';
    if (city === 'S.P.B' || city === 'SPB') return 'სანქტ-პეტერბურგი';
    if (city.toLowerCase() === 'tbilisi') return 'თბილისი';
    if (city.toLowerCase() === 'batumi') return 'ბათუმი';
    return city || 'მითითებული არ არის';
  }

  function paymentLabel(item) {
    if (item.payment_kind === 'mixed') return 'შერეული გადახდა';
    if (item.payment_kind === 'due') return 'მიღებისას';
    if (item.payment_is_card) return 'ბარათით გადახდილია';
    return 'გადახდილია';
  }

  function orderDate(item) {
    return item.order_label || item.flight || item.date_label || 'მითითებული არ არის';
  }

  function toast(message, type) {
    const node = document.createElement('div');
    node.className = `toast-message ${type || ''}`;
    node.textContent = message;
    els.toastStack.appendChild(node);
    window.setTimeout(() => {
      node.style.opacity = '0';
      node.style.transform = 'translateY(8px)';
    }, 2600);
    window.setTimeout(() => node.remove(), 3100);
  }

  function getInput(id) {
    return document.getElementById(id);
  }

  function syncDestinationCityControls(value) {
    state.destinationCity = value || 'all';
    document.querySelectorAll('.city-tab').forEach((node) => {
      node.classList.toggle('active', node.dataset.destinationCity === state.destinationCity);
    });
  }

  function buildParams() {
    const params = new URLSearchParams({
      page: String(state.page),
      per_page: String(state.perPage),
      destination_city: state.destinationCity,
      origin_city: state.originCity,
      range: state.range === 'custom' ? '' : state.range,
    });

    const map = {
      filterSearch: 'search',
      filterPayment: 'payment',
      filterStatus: 'status',
      filterSender: 'sender',
      filterSenderPhone: 'sender_phone',
      filterRecipient: 'recipient',
      filterRecipientPhone: 'recipient_phone',
    };

    Object.entries(map).forEach(([id, key]) => {
      const value = getInput(id).value.trim();
      if (value) params.set(key, value);
    });

    if (state.range === 'custom') {
      const from = getInput('filterDateFrom').value;
      const to = getInput('filterDateTo').value;
      if (from) params.set('date_from', from);
      if (to) params.set('date_to', to);
    }

    return params;
  }

  function setLoading(isLoading, replace) {
    state.loading = isLoading;
    els.loadMore.disabled = isLoading;
    if (isLoading && replace) {
      els.list.innerHTML = '<div class="loading-state">ამანათები იტვირთება...</div>';
    }
  }

  function updateAnalytics(data) {
    const analytics = data || {};
    metrics.total.textContent = formatNumber(analytics.total);
    metrics.active.textContent = formatNumber(analytics.active);
    metrics.issued.textContent = formatNumber(analytics.issued);
    metrics.weight.textContent = formatNumber(analytics.weight);
    metrics.profitGel.textContent = formatNumber(analytics.profit_gel);
    metrics.profitRub.textContent = formatNumber(analytics.profit_rub);
    metrics.dueGel.textContent = formatNumber(analytics.due_gel);
    metrics.dueRub.textContent = formatNumber(analytics.due_rub);
    metrics.moscow.textContent = formatNumber(analytics.moscow);
    metrics.spb.textContent = formatNumber(analytics.spb);
    metrics.tbilisi.textContent = formatNumber(analytics.tbilisi);
    metrics.batumi.textContent = formatNumber(analytics.batumi);
  }

  function parcelTemplate(item) {
    const issued = item.delivery === 'yes';
    const ready = item.departure_status === '+';
    const paymentClass = item.payment_kind === 'mixed' ? 'mixed' : (item.payment_kind === 'due' ? 'due' : 'paid');
    const compactClass = issued ? 'issued compact' : '';
    const orderLabel = orderDate(item);
    const routeText = `${cityLabel(item.where_from)} -> ${cityLabel(item.city)}`;
    const statusText = issued ? 'გაცემულია' : 'მუშაობაში';

    return `
      <article class="parcel-card ${compactClass}" data-id="${escapeHtml(item.id)}">
        <div class="parcel-main">
          <div class="parcel-head">
            <div class="parcel-head-main">
              <div class="parcel-title">
                <span class="parcel-number"><i class="bi bi-box-seam"></i>#${escapeHtml(item.number)}</span>
                <span class="status-pill ${issued ? '' : 'active'}">
                  <i class="bi ${issued ? 'bi-check-circle' : 'bi-clock'}"></i>
                  ${escapeHtml(statusText)}
                </span>
                ${ready ? '<span class="ready-pill"><i class="bi bi-send-check"></i>მზადაა</span>' : ''}
              </div>
              <div class="route-line">
                <strong>${escapeHtml(routeText)}</strong>
              </div>
            </div>
            <div class="parcel-date-card">
              <span>გაფორმდა</span>
              <strong>${escapeHtml(orderLabel)}</strong>
            </div>
          </div>

          <div class="compact-summary">
            <div>
              <span class="data-label">მიმღები</span>
              <strong>${escapeHtml(item.recipient || 'მითითებული არ არის')}</strong>
            </div>
            <div>
              <span class="data-label">ტელეფონი</span>
              <strong>${escapeHtml(item.recipient_phone || 'მითითებული არ არის')}</strong>
            </div>
            <div>
              <span class="data-label">გადახდა</span>
              <strong>${escapeHtml(item.cost || 'მითითებული არ არის')}</strong>
            </div>
          </div>

          <div class="person-grid">
            <div class="person-panel">
              <div class="person-role"><i class="bi bi-person-up"></i>გამგზავნი</div>
              <div class="person-data">
                <div>
                  <span class="data-label">სახელი გვარი</span>
                  <span class="data-value">${escapeHtml(item.sender)}</span>
                </div>
                <div>
                  <span class="data-label">ტელეფონი</span>
                  <span class="data-value">${escapeHtml(item.sender_phone)}</span>
                </div>
              </div>
            </div>
            <div class="person-panel">
              <div class="person-role"><i class="bi bi-person-down"></i>მიმღები</div>
              <div class="person-data">
                <div>
                  <span class="data-label">სახელი გვარი</span>
                  <span class="data-value">${escapeHtml(item.recipient)}</span>
                </div>
                <div>
                  <span class="data-label">ტელეფონი</span>
                  <span class="data-value">${escapeHtml(item.recipient_phone)}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="route-strip">
            <div class="route-city">
              <span>საიდან</span>
              <strong>${escapeHtml(cityLabel(item.where_from))}</strong>
            </div>
            <div class="route-arrow"><i class="bi bi-arrow-right"></i></div>
            <div class="route-city">
              <span>სად</span>
              <strong>${escapeHtml(cityLabel(item.city))}</strong>
            </div>
          </div>

          <div class="parcel-details">
            <div class="detail-item">
              <span class="data-label">გადახდა</span>
              <span class="pay-pill ${paymentClass}">
                <i class="bi ${item.payment_kind === 'mixed' ? 'bi-shuffle' : (item.payment_kind === 'due' ? 'bi-exclamation-circle' : 'bi-check-circle')}"></i>
                ${escapeHtml(paymentLabel(item))}
              </span>
              <span class="data-value">${escapeHtml(item.cost)}</span>
            </div>
            <div class="detail-item">
              <span class="data-label">წონა</span>
              <span class="data-value weight-value"><i class="bi bi-box"></i> ${escapeHtml(item.weight)} კგ</span>
            </div>
            <div class="detail-item">
              <span class="data-label">ღირებულება</span>
              <span class="data-value">${escapeHtml(item.responsibility || 'მითითებული არ არის')}</span>
            </div>
          </div>

          <div class="inventory-box">
            <span class="data-label">შიგთავსის აღწერა</span>
            <span class="data-value">${escapeHtml(item.inventory || 'აღწერა არ არის')}</span>
          </div>

          <div class="extra-grid">
            <div class="extra-item">პასპორტი<strong>${escapeHtml(item.passport || 'მითითებული არ არის')}</strong></div>
            <div class="extra-item">ტვირთის ღირებულება<strong>${escapeHtml(item.responsibility || 'მითითებული არ არის')}</strong></div>
            <div class="extra-item">ჩანაწერის ID<strong>${escapeHtml(item.id)}</strong></div>
          </div>
        </div>

        <aside class="parcel-side">
          <div class="side-status-card">
            <span class="data-label">სტატუსი</span>
            <strong>${escapeHtml(statusText)}</strong>
            <small>${escapeHtml(paymentLabel(item))}</small>
          </div>
          <button class="image-shell" type="button" data-action="image" aria-label="ფოტოს გახსნა">
            <img class="image-thumb" src="${escapeHtml(item.thumbnail)}" alt="">
            <img class="image-full" src="${escapeHtml(item.image)}" alt="ამანათის ფოტო" loading="lazy" decoding="async">
            <span class="image-badge"><i class="bi bi-zoom-in"></i> ფოტო</span>
          </button>
          <div class="side-facts">
            <div>
              <span>გადახდა</span>
              <strong>${escapeHtml(item.cost || '-')}</strong>
            </div>
            <div>
              <span>წონა</span>
              <strong>${escapeHtml(item.weight || '-')} კგ</strong>
            </div>
          </div>
          <div class="action-row">
            <button class="icon-button edit" type="button" data-action="edit" title="რედაქტირება">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="icon-button delete" type="button" data-action="delete" title="წაშლა">
              <i class="bi bi-trash3"></i>
            </button>
            ${issued ? '' : `
              <button class="icon-button issue" type="button" data-action="issue" title="გაცემა">
                <i class="bi bi-box-arrow-in-down"></i>
              </button>
            `}
          </div>
          <button class="toggle-details" type="button" data-action="toggle">
            ${issued ? 'სრულად ნახვა' : 'დეტალების დაკეცვა'}
          </button>
        </aside>
      </article>
    `;
  }

  function hydrateImages(scope) {
    scope.querySelectorAll('.image-full').forEach((img) => {
      if (img.complete) {
        img.closest('.image-shell').classList.add('loaded');
      } else {
        img.addEventListener('load', () => img.closest('.image-shell').classList.add('loaded'), { once: true });
      }
    });
  }

  function renderItems(items, replace) {
    if (replace) {
      els.list.innerHTML = '';
      state.items.clear();
    }

    items.forEach((item) => {
      state.items.set(String(item.id), item);
      els.list.insertAdjacentHTML('beforeend', parcelTemplate(item));
    });

    hydrateImages(els.list);

    if (!els.list.children.length) {
      els.list.innerHTML = '<div class="empty-state">ჩანაწერები ვერ მოიძებნა</div>';
    }
  }

  async function loadParcels(options) {
    if (state.loading) return;
    const replace = Boolean(options && options.replace);
    setLoading(true, replace);

    try {
      const response = await fetch(`/api/all-new/parcels?${buildParams().toString()}`);
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'ჩატვირთვის შეცდომა');
      }

      renderItems(data.items, replace);
      updateAnalytics(data.analytics);

      const pagination = data.pagination;
      state.hasMore = Boolean(pagination.has_more);
      els.loadMore.hidden = !state.hasMore;
      els.resultTitle.textContent = `ნაპოვნია ${formatNumber(pagination.total)}`;
      els.resultMeta.textContent = `ნაჩვენებია ${formatNumber(Math.min(pagination.page * pagination.per_page, pagination.total))}`;
    } catch (error) {
      els.list.innerHTML = '<div class="empty-state">სიის ჩატვირთვა ვერ მოხერხდა</div>';
      toast(error.message, 'error');
    } finally {
      setLoading(false, false);
    }
  }

  function reloadFromFirstPage() {
    state.page = 1;
    loadParcels({ replace: true });
  }

  function debounce(fn, wait) {
    let timer = 0;
    return function () {
      window.clearTimeout(timer);
      timer = window.setTimeout(fn, wait);
    };
  }

  function openImage(item) {
    els.lightboxImage.src = item.image;
    els.lightboxCaption.textContent = `#${item.number} ${item.sender} -> ${item.recipient}`;
    els.lightbox.classList.add('open');
    els.lightbox.setAttribute('aria-hidden', 'false');
  }

  function closeImage() {
    els.lightbox.classList.remove('open');
    els.lightbox.setAttribute('aria-hidden', 'true');
    els.lightboxImage.src = '';
  }

  function openEdit(item) {
    document.getElementById('editIdInput').value = item.id;
    document.getElementById('editSenderInput').value = item.sender;
    document.getElementById('editSenderPhoneInput').value = item.sender_phone;
    document.getElementById('editRecipientInput').value = item.recipient;
    document.getElementById('editRecipientPhoneInput').value = item.recipient_phone;
    document.getElementById('editInventoryTextarea').value = item.inventory;
    document.getElementById('editWeightInput').value = item.weight;
    document.getElementById('editResponsibilityInput').value = item.responsibility;
    document.getElementById('editPassportInput').value = item.passport;
    document.getElementById('editCostInput').value = item.cost;
    document.getElementById('editDepartureStatusCheckbox').checked = item.departure_status === '+';
    document.getElementById('editTitle').textContent = `ამანათი #${item.number}`;

    const citySelect = document.getElementById('editCitySelect');
    if (item.city && !Array.from(citySelect.options).some((option) => option.value === item.city)) {
      const option = document.createElement('option');
      option.value = item.city;
      option.textContent = cityLabel(item.city);
      citySelect.appendChild(option);
    }
    citySelect.value = item.city;

    els.editOverlay.classList.add('open');
    els.editOverlay.setAttribute('aria-hidden', 'false');
  }

  function closeEdit() {
    els.editOverlay.classList.remove('open');
    els.editOverlay.setAttribute('aria-hidden', 'true');
    document.getElementById('editPhotoInput').value = '';
  }

  function openAddParcel() {
    if (!els.addFrame.getAttribute('src')) {
      els.addFrame.setAttribute('src', '/add?embedded=1');
    }
    els.addOverlay.classList.add('open');
    els.addOverlay.setAttribute('aria-hidden', 'false');
  }

  function closeAddParcel(options) {
    const config = options || {};
    if (addCloseResolve) {
      const resolve = addCloseResolve;
      addCloseResolve = null;
      setAddCloseChoice(false);
      resolve('cancel');
    }
    if (config.clear) {
      resetAddParcelForm();
    }
    els.addOverlay.classList.remove('open');
    els.addOverlay.setAttribute('aria-hidden', 'true');
  }

  function resetAddParcelForm() {
    if (!els.addFrame.contentWindow) return;
    els.addFrame.contentWindow.postMessage({ type: 'vipost:reset-add-form' }, window.location.origin);
  }

  function setAddCloseChoice(open) {
    els.addCloseChoice.classList.toggle('open', open);
    els.addCloseChoice.setAttribute('aria-hidden', open ? 'false' : 'true');
  }

  function resolveAddCloseChoice(choice) {
    if (!addCloseResolve) return;
    const resolve = addCloseResolve;
    addCloseResolve = null;
    setAddCloseChoice(false);
    resolve(choice);
  }

  function askAddCloseChoice() {
    if (addCloseResolve) return Promise.resolve('cancel');
    setAddCloseChoice(true);
    return new Promise((resolve) => {
      addCloseResolve = resolve;
    });
  }

  async function requestCloseAddParcel() {
    if (!els.addOverlay.classList.contains('open')) return;
    const choice = await askAddCloseChoice();
    if (choice === 'clear') {
      closeAddParcel({ clear: true });
    }
    if (choice === 'keep') {
      closeAddParcel();
    }
  }

  async function submitEdit(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('id', document.getElementById('editIdInput').value);
    formData.append('sender', document.getElementById('editSenderInput').value);
    formData.append('sender_phone', document.getElementById('editSenderPhoneInput').value);
    formData.append('recipient', document.getElementById('editRecipientInput').value);
    formData.append('recipient_phone', document.getElementById('editRecipientPhoneInput').value);
    formData.append('inventory', document.getElementById('editInventoryTextarea').value);
    formData.append('weight', document.getElementById('editWeightInput').value);
    formData.append('responsibility', document.getElementById('editResponsibilityInput').value);
    formData.append('passport', document.getElementById('editPassportInput').value);
    formData.append('cost', document.getElementById('editCostInput').value);
    formData.append('city', document.getElementById('editCitySelect').value);
    formData.append('departureStatus', document.getElementById('editDepartureStatusCheckbox').checked ? '+' : '-');

    const photo = document.getElementById('editPhotoInput').files[0];
    if (photo) formData.append('photo', photo);

    try {
      const response = await fetch('/edit_parcel', { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'შენახვა ვერ მოხერხდა');
      }
      toast('ცვლილებები შენახულია', 'success');
      closeEdit();
      reloadFromFirstPage();
    } catch (error) {
      toast(error.message, 'error');
    }
  }

  async function deleteParcel(item) {
    if (!window.confirm(`წავშალოთ ამანათი #${item.number}?`)) return;
    try {
      const response = await fetch('/removing_from_the_list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: item.id }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'წაშლა ვერ მოხერხდა');
      }
      toast('ჩანაწერი წაშლილია', 'success');
      reloadFromFirstPage();
    } catch (error) {
      toast(error.message, 'error');
    }
  }

  async function issueParcel(item) {
    if (!window.confirm(`გავცეთ ამანათი #${item.number}?`)) return;
    try {
      const response = await fetch('/delivery_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: item.id }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'სტატუსის შეცვლა ვერ მოხერხდა');
      }
      toast('ამანათი გაცემულად მოინიშნა', 'success');
      reloadFromFirstPage();
    } catch (error) {
      toast(error.message, 'error');
    }
  }

  function handleCardClick(event) {
    const actionNode = event.target.closest('[data-action]');
    if (!actionNode) return;

    const card = event.target.closest('.parcel-card');
    const item = state.items.get(card.dataset.id);
    if (!item) return;

    const action = actionNode.dataset.action;
    if (action === 'image') openImage(item);
    if (action === 'edit') openEdit(item);
    if (action === 'delete') deleteParcel(item);
    if (action === 'issue') issueParcel(item);
    if (action === 'toggle') {
      card.classList.toggle('compact');
      actionNode.textContent = card.classList.contains('compact') ? 'სრულად ნახვა' : 'დეტალების დაკეცვა';
    }
  }

  function bindFilters() {
    const debouncedReload = debounce(reloadFromFirstPage, 320);
    filterIds.forEach((id) => {
      const input = getInput(id);
      input.addEventListener(input.tagName === 'SELECT' ? 'change' : 'input', debouncedReload);
    });

    document.getElementById('filterOriginCitySelect').addEventListener('change', (event) => {
      state.originCity = event.target.value || 'all';
      reloadFromFirstPage();
    });

    document.querySelectorAll('.city-tab').forEach((button) => {
      button.addEventListener('click', () => {
        syncDestinationCityControls(button.dataset.destinationCity);
        reloadFromFirstPage();
      });
    });

    document.querySelectorAll('.range-tab').forEach((button) => {
      button.addEventListener('click', () => {
        document.querySelectorAll('.range-tab').forEach((node) => node.classList.remove('active'));
        button.classList.add('active');
        state.range = button.dataset.range;
        els.customDates.hidden = state.range !== 'custom';
        reloadFromFirstPage();
      });
    });

    document.getElementById('resetFilters').addEventListener('click', () => {
      filterIds.forEach((id) => {
        getInput(id).value = '';
      });
      state.destinationCity = 'all';
      state.originCity = 'all';
      state.range = '';
      document.getElementById('filterOriginCitySelect').value = 'all';
      syncDestinationCityControls('all');
      document.querySelectorAll('.range-tab').forEach((node) => node.classList.toggle('active', node.dataset.range === ''));
      els.customDates.hidden = true;
      reloadFromFirstPage();
    });
  }

  function bindStaticActions() {
    els.list.addEventListener('click', handleCardClick);
    els.loadMore.addEventListener('click', () => {
      if (!state.hasMore) return;
      state.page += 1;
      loadParcels({ replace: false });
    });
    document.getElementById('refreshList').addEventListener('click', reloadFromFirstPage);
    document.getElementById('closeLightbox').addEventListener('click', closeImage);
    els.lightbox.addEventListener('click', (event) => {
      if (event.target === els.lightbox) closeImage();
    });
    document.getElementById('closeEdit').addEventListener('click', closeEdit);
    document.getElementById('cancelEdit').addEventListener('click', closeEdit);
    els.editOverlay.addEventListener('click', (event) => {
      if (event.target === els.editOverlay) closeEdit();
    });
    document.getElementById('openAddParcel').addEventListener('click', openAddParcel);
    document.getElementById('closeAddParcel').addEventListener('click', requestCloseAddParcel);
    els.addOverlay.addEventListener('click', (event) => {
      if (event.target === els.addOverlay) requestCloseAddParcel();
    });
    els.addCloseChoice.addEventListener('click', (event) => {
      if (event.target === els.addCloseChoice) {
        resolveAddCloseChoice('cancel');
        return;
      }
      const choiceButton = event.target.closest('[data-add-close-choice]');
      if (choiceButton) resolveAddCloseChoice(choiceButton.dataset.addCloseChoice);
    });
    window.addEventListener('message', (event) => {
      if (event.origin !== window.location.origin) return;
      if (!event.data || event.data.type !== 'vipost:parcel-created') return;
      closeAddParcel();
      toast('ამანათი დაემატა', 'success');
      reloadFromFirstPage();
    });
    els.editForm.addEventListener('submit', submitEdit);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        if (els.addCloseChoice.classList.contains('open')) {
          resolveAddCloseChoice('cancel');
          return;
        }
        if (els.addOverlay.classList.contains('open')) {
          requestCloseAddParcel();
          return;
        }
        closeImage();
        closeEdit();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    bindFilters();
    bindStaticActions();
    loadParcels({ replace: true });
  });
})();
