// Global State and Helpers for Antigravity Rental Website
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Load Saved Favorites from localStorage
  window.updateSavedCount = function () {
    try {
      const saved = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      const countBadges = document.querySelectorAll(".saved-count-badge");
      countBadges.forEach(b => {
        b.textContent = saved.length;
        b.style.display = saved.length > 0 ? "inline-flex" : "none";
      });

      // Update heart button states across all cards
      document.querySelectorAll("[data-save-btn]").forEach(btn => {
        const id = parseInt(btn.getAttribute("data-property-id"));
        const icon = btn.querySelector("svg");
        if (saved.includes(id)) {
          btn.classList.add("text-red-500");
          if (icon) icon.classList.add("fill-red-500", "text-red-500");
        } else {
          btn.classList.remove("text-red-500");
          if (icon) icon.classList.remove("fill-red-500", "text-red-500");
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.toggleSaveProperty = function (id) {
    id = parseInt(id);
    try {
      let saved = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      if (saved.includes(id)) {
        saved = saved.filter(item => item !== id);
      } else {
        saved.push(id);
      }
      localStorage.setItem("saved_properties_ids", JSON.stringify(saved));
      window.updateSavedCount();
      if (window.renderSavedDrawer) {
        window.renderSavedDrawer();
      }
    } catch (e) {
      console.error(e);
    }
  };

  window.updateSavedCount();

  // Modals management
  window.openModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("hidden");
      el.classList.add("flex");
      document.body.style.overflow = "hidden";
      if (window.lucide) window.lucide.createIcons();
    }
  };

  window.closeModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("hidden");
      el.classList.remove("flex");
      document.body.style.overflow = "auto";
    }
  };

  window.openPropertyDetailById = function (id) {
    id = parseInt(id);
    if (window.allPropertiesData) {
      const prop = window.allPropertiesData.find(p => p.id === id);
      if (prop) {
        window.openPropertyDetail(prop);
      }
    }
  };

  // Property Detail Modal Populator
  window.openPropertyDetail = function (propertyData) {
    if (typeof propertyData === "string") {
      try { propertyData = JSON.parse(propertyData); } catch (e) {}
    }
    window.currentModalProperty = propertyData;
    const modal = document.getElementById("propertyDetailModal");
    if (!modal) return;

    const isAr = document.documentElement.dir === "rtl";
    const title = (isAr && propertyData.title_ar) ? propertyData.title_ar : propertyData.title;
    const desc = (isAr && propertyData.description_ar) ? propertyData.description_ar : propertyData.description;

    // Safe helper to set text content
    const setElText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val !== undefined && val !== null ? val : "";
    };

    // Set Text Content
    setElText("modalTitle", title);
    setElText("modalAddress", `${propertyData.address}, ${propertyData.city}, ${propertyData.state} ${propertyData.zip_code}`);
    setElText("modalBeds", `${propertyData.bedrooms} Beds`);
    setElText("modalBaths", `${propertyData.bathrooms} Baths`);
    setElText("modalSqft", `${propertyData.area_sqft} Ft²`);
    setElText("modalBadge", propertyData.badge || "Perfect Fit");
    setElText("modalDesc", desc);

    // Pricing in EGP
    const rentVal = propertyData.price_egp || propertyData.price || 2500;
    const priceText = `${rentVal.toLocaleString()} ج.م`;
    setElText("modalPrice", priceText);
    setElText("modalPriceSuffix", "/ شهر");

    // Cost Breakdown in EGP
    const baseRent = rentVal;
    const secDep = propertyData.deposit_egp || 2000;
    const totalMove = baseRent + secDep;
    setElText("modalBaseRent", `${baseRent.toLocaleString()} ج.م`);
    setElText("modalSecDeposit", `${secDep.toLocaleString()} ج.م`);
    setElText("modalTotalMoveIn", `${totalMove.toLocaleString()} ج.م`);

    // Agent Details & Instant WhatsApp
    setElText("modalAgentName", propertyData.agent_name || "مشرف السكن");
    setElText("modalAgentPhone", propertyData.agent_phone || "+201012345678");
    setElText("modalAgentEmail", propertyData.agent_email || "contact@sakancairo.com");
    
    const avatarEl = document.getElementById("modalAgentAvatar");
    if (avatarEl && propertyData.agent_avatar) {
      avatarEl.src = propertyData.agent_avatar;
    }

    const whatsAppEl = document.getElementById("modalWhatsAppLink");
    if (whatsAppEl && propertyData.whatsapp_url) {
      whatsAppEl.href = propertyData.whatsapp_url;
    }

    const callLink = document.getElementById("modalCallLink");
    if (callLink && propertyData.agent_phone) {
      callLink.href = `tel:${propertyData.agent_phone}`;
    }

    // Amenities List
    const amenitiesContainer = document.getElementById("modalAmenities");
    if (amenitiesContainer && propertyData.amenities) {
      amenitiesContainer.innerHTML = propertyData.amenities.map(a => `
        <div class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200/60 text-slate-700 text-xs font-medium">
          <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span>${a}</span>
        </div>
      `).join('');
    }

    // Family Highlights
    const familyContainer = document.getElementById("modalFamilyHighlights");
    if (familyContainer && propertyData.family_highlights && propertyData.family_highlights.length > 0) {
      familyContainer.parentElement.style.display = "block";
      familyContainer.innerHTML = propertyData.family_highlights.map(h => `
        <li class="flex items-start gap-2 text-xs text-slate-600">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5"></i>
          <span>${h}</span>
        </li>
      `).join('');
    } else if (familyContainer) {
      familyContainer.parentElement.style.display = "none";
    }

    // Photos Gallery
    const images = propertyData.images && propertyData.images.length > 0
      ? propertyData.images
      : ["https://images.pexels.com/photos/8134745/pexels-photo-8134745.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200"];

    const mainPhoto = document.getElementById("modalMainPhoto");
    mainPhoto.src = images[0];

    const thumbsContainer = document.getElementById("modalThumbnails");
    if (thumbsContainer) {
      thumbsContainer.innerHTML = images.map((img, idx) => `
        <button onclick="document.getElementById('modalMainPhoto').src = '${img}'" 
          class="shrink-0 w-20 h-14 rounded-xl overflow-hidden border-2 border-transparent hover:border-blue-500 focus:border-blue-500 transition cursor-pointer">
          <img src="${img}" class="w-full h-full object-cover" />
        </button>
      `).join('');
    }

    // Tour Form hidden property ID
    const tourPropInput = document.getElementById("id_property");
    if (tourPropInput) {
      tourPropInput.value = propertyData.id;
    }

    // Save button state in modal
    const saveBtn = document.getElementById("modalSaveBtn");
    if (saveBtn) {
      saveBtn.setAttribute("data-property-id", propertyData.id);
      saveBtn.onclick = function () {
        window.toggleSaveProperty(propertyData.id);
      };
    }

    window.openModal("propertyDetailModal");
    window.updateSavedCount();
  };

  // Copy payment account text (InstaPay / Vodafone Cash)
  window.copyPaymentText = function (text, btn) {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      const span = btn.querySelector("span");
      const original = span ? span.textContent : "";
      if (span) span.textContent = "تم النسخ ✓";
      btn.classList.add("text-emerald-600");
      setTimeout(() => {
        if (span) span.textContent = original;
        btn.classList.remove("text-emerald-600");
      }, 2000);
    }).catch(err => {
      console.error("Clipboard copy failed:", err);
    });
  };

  // Preview uploaded receipt image
  window.previewReceiptImage = function (input) {
    if (input.files && input.files[0]) {
      const file = input.files[0];
      const reader = new FileReader();
      reader.onload = function (e) {
        const previewImg = document.getElementById("receiptPreviewImg");
        const fileName = document.getElementById("receiptFileName");
        const placeholder = document.getElementById("receiptUploadPlaceholder");
        const container = document.getElementById("receiptPreviewContainer");

        if (previewImg) previewImg.src = e.target.result;
        if (fileName) fileName.textContent = file.name;
        if (placeholder) placeholder.classList.add("hidden");
        if (container) {
          container.classList.remove("hidden");
          container.classList.add("flex");
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // Tour Booking Form AJAX & Confetti
  const tourForm = document.getElementById("tourBookingForm");
  if (tourForm) {
    tourForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(tourForm);
      const submitBtn = tourForm.querySelector("button[type='submit']");
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = "جاري إرسال الطلب وإيصال السداد...";

      fetch("/tours/book/?format=json", {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        if (data.success) {
          // Trigger Confetti Celebration!
          if (window.confetti) {
            window.confetti({
              particleCount: 120,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
          const successBox = document.getElementById("tourSuccessAlert");
          if (successBox) {
            if (data.message) {
              const msgSpan = successBox.querySelector("span");
              if (msgSpan) msgSpan.textContent = data.message;
            }
            successBox.classList.remove("hidden");
            setTimeout(() => { successBox.classList.add("hidden"); }, 6000);
          }
          tourForm.reset();
          const placeholder = document.getElementById("receiptUploadPlaceholder");
          const container = document.getElementById("receiptPreviewContainer");
          if (placeholder) placeholder.classList.remove("hidden");
          if (container) {
            container.classList.add("hidden");
            container.classList.remove("flex");
          }
        } else {
          alert(data.message || "يرجى التأكد من ملء الحقول المطلوبة وإرفاق صورة إيصال التحويل بشكل صحيح.");
        }
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        console.error(err);
        alert("حدث خطأ أثناء الاتصال بالخادم، يرجى المحاولة مرة أخرى.");
      });
    });
  }

  // Interactive Map Rendering (Cairo Coordinates & EGP Student Housing)
  window.initInteractiveMap = function (properties) {
    const mapContainer = document.getElementById("interactiveMapCanvas");
    if (!mapContainer || !properties || properties.length === 0) return;

    const validProps = properties.filter(p => p.lat && p.lng && !isNaN(parseFloat(p.lat)) && !isNaN(parseFloat(p.lng)));
    if (validProps.length === 0) return;

    const lats = validProps.map(p => parseFloat(p.lat));
    const lngs = validProps.map(p => parseFloat(p.lng));

    // Calculate dynamic bounding box around Cairo student housing properties
    let minLat = Math.min(...lats);
    let maxLat = Math.max(...lats);
    let minLng = Math.min(...lngs);
    let maxLng = Math.max(...lngs);

    // Add padding around coordinates for clean visual framing
    const latSpan = maxLat - minLat || 0.05;
    const lngSpan = maxLng - minLng || 0.05;
    minLat -= latSpan * 0.15;
    maxLat += latSpan * 0.15;
    minLng -= lngSpan * 0.15;
    maxLng += lngSpan * 0.15;

    const getCoordinates = (latStr, lngStr) => {
      const lat = parseFloat(latStr);
      const lng = parseFloat(lngStr);
      const x = ((lng - minLng) / (maxLng - minLng || 1)) * 76 + 12;
      const y = 88 - ((lat - minLat) / (maxLat - minLat || 1)) * 76;
      return { x: Math.max(8, Math.min(92, x)), y: Math.max(10, Math.min(90, y)) };
    };

    mapContainer.innerHTML = validProps.map(p => {
      const coords = getCoordinates(p.lat, p.lng);
      const priceVal = Number(p.price_egp || p.price || 0);
      const priceTag = `${priceVal.toLocaleString()} ج.م`;
      const title = p.title_ar || p.title || 'سكن طلاب';
      const imgSrc = (p.images && p.images.length > 0) ? p.images[0] : 'https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg';
      const dist = p.distance_to_university || '';
      const rentalDisplay = p.rental_type_display || '';

      return `
        <div class="absolute cursor-pointer transition-transform duration-200 hover:scale-110 hover:z-30 group"
          style="left: ${coords.x}%; top: ${coords.y}%;"
          onclick='window.openPropertyDetail(${JSON.stringify(p)})'>
          
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white text-slate-900 border border-slate-300 shadow-lg font-bold text-xs hover:bg-emerald-600 hover:text-white transition">
            <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 group-hover:text-white"></i>
            <span>${priceTag}</span>
          </div>

          <!-- Hover Card Preview (Arabic RTL) -->
          <div class="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 bg-white rounded-2xl p-2.5 shadow-2xl border border-slate-100 z-40 text-right" dir="rtl">
            <img src="${imgSrc}" class="w-full h-24 object-cover rounded-xl mb-2" alt="${title}" />
            <div class="text-xs font-bold text-slate-900 truncate">${title}</div>
            <div class="text-[11px] text-emerald-600 font-bold mt-0.5">${rentalDisplay}</div>
            <div class="text-[10px] text-slate-500 mt-0.5">${p.city} ${dist ? '• ' + dist : ''}</div>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  };

  // Saved Properties Drawer
  window.renderSavedDrawer = function () {
    const container = document.getElementById("savedDrawerList");
    if (!container || !window.allPropertiesData) return;

    try {
      const savedIds = JSON.parse(localStorage.getItem("saved_properties_ids") || "[]");
      const savedList = window.allPropertiesData.filter(p => savedIds.includes(p.id));

      if (savedList.length === 0) {
        container.innerHTML = `
          <div class="text-center py-12 text-slate-400">
            <i data-lucide="heart" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
            <p class="text-sm font-semibold text-slate-600">لم تقم بحفظ أي سكن في المفضلة بعد.</p>
            <p class="text-xs text-slate-400 mt-1">اضغط على أيقونة القلب في أي إعلان لحفظه هنا والرجوع إليه لاحقاً.</p>
          </div>
        `;
      } else {
        container.innerHTML = savedList.map(p => {
          const priceVal = Number(p.price_egp || p.price || 0);
          const imgSrc = (p.images && p.images.length > 0) ? p.images[0] : 'https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg';
          const title = p.title_ar || p.title || 'سكن طلاب';
          const location = p.city || 'القاهرة';

          return `
          <div class="flex items-center gap-3 p-3 rounded-2xl border border-slate-200/80 hover:border-emerald-300 hover:shadow-xs bg-white transition cursor-pointer"
            onclick="window.openPropertyDetailById(${p.id})">
            <img src="${imgSrc}" class="w-16 h-16 rounded-xl object-cover shrink-0" alt="${title}" />
            <div class="flex-1 min-w-0">
              <h4 class="text-xs font-bold text-slate-800 truncate">${title}</h4>
              <p class="text-[11px] text-slate-500 mt-0.5">${location}</p>
              <div class="text-xs font-extrabold text-emerald-600 mt-1">${priceVal.toLocaleString()} ج.م / شهر</div>
            </div>
            <button onclick="event.stopPropagation(); window.toggleSaveProperty(${p.id});" class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition cursor-pointer" title="حذف من المفضلة">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
          `;
        }).join('');
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (e) {
      console.error("Error in renderSavedDrawer:", e);
    }
  };
});
