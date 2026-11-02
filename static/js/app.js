// Application State
let currentTab = 'recommended';
let selectedInterests = ['Coding and Programming', 'Artificial Intelligence', 'Business and Entrepreneurship'];
let currentDepartment = 'All';
let currentSearchQuery = '';
let currentQuickFilter = '';
let searchDebounceTimer = null;
let allEventsCache = [];
let allEmailsCache = [];

// Auto-sync countdown variables
let nextSyncRemainingSeconds = 1800;
let autoSyncInterval = null;

// Bookmarks (Saved events) in localStorage
let savedEventIds = [];
try {
  savedEventIds = JSON.parse(localStorage.getItem('caias_saved_events') || '[]');
} catch (e) {
  savedEventIds = [];
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  updateInterestPillStyles();
  updateSavedBadge();
  fetchAppStatus();
  loadEvents();
  startAutoSyncCountdown();
});

// Auto-Sync Countdown Loop (ticks every second)
function startAutoSyncCountdown() {
  if (autoSyncInterval) clearInterval(autoSyncInterval);
  
  autoSyncInterval = setInterval(() => {
    if (nextSyncRemainingSeconds > 0) {
      nextSyncRemainingSeconds--;
      updateAutoSyncDisplay();
    } else {
      // Countdown reached 0: trigger sync and refresh data
      nextSyncRemainingSeconds = 1800;
      fetch('/api/cron_sync')
        .then(() => {
          fetchAppStatus();
          loadEvents();
        })
        .catch(() => {
          fetchAppStatus();
          loadEvents();
        });
    }
  }, 1000);
}

function updateAutoSyncDisplay() {
  const display = document.getElementById('autoSyncDisplay');
  if (!display) return;
  const mins = Math.floor(nextSyncRemainingSeconds / 60);
  const secs = nextSyncRemainingSeconds % 60;
  display.textContent = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// Fetch system status and counters
async function fetchAppStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    if (data.user_email) {
      const emailElem = document.getElementById('headerUserEmail');
      if (emailElem) emailElem.textContent = data.user_email;
    }
    if (data.last_synced) {
      const lastSyncElem = document.getElementById('lastSyncedDisplay');
      if (lastSyncElem) lastSyncElem.textContent = data.last_synced;
    }

    if (data.next_sync_seconds !== undefined && data.next_sync_seconds > 0) {
      nextSyncRemainingSeconds = data.next_sync_seconds;
      updateAutoSyncDisplay();
    } else {
      // If overdue on page load, trigger background sync
      fetch('/api/cron_sync').catch(() => {});
    }

    // Update Counter Numbers
    if (data.active_events_count !== undefined) {
      document.getElementById('statActiveCount').textContent = data.active_events_count;
    }
    if (data.expired_events_count !== undefined) {
      document.getElementById('statExpiredCount').textContent = data.expired_events_count;
      document.getElementById('tabBadge-expired').textContent = data.expired_events_count;
    }
    document.getElementById('statEnrichedCount').textContent = data.enriched_calendar_count || 0;
    document.getElementById('statStandaloneCount').textContent = data.standalone_events_count || 0;

    // Badges in tabs
    document.getElementById('tabBadge-live-updates').textContent = data.enriched_calendar_count || 0;
    document.getElementById('tabBadge-nlp').textContent = data.emails_analyzed_count || 0;
    if (data.calendar_count) {
      document.getElementById('tabBadge-calendar-all').textContent = data.calendar_count;
    }
  } catch (err) {
    console.error("Status fetch error:", err);
  }
}

// Load events from backend
async function loadEvents() {
  const loading = document.getElementById('loadingState');
  const empty = document.getElementById('emptyState');
  const grid = document.getElementById('eventsGrid');

  loading.classList.remove('hidden');
  empty.classList.add('hidden');
  grid.innerHTML = '';

  const params = new URLSearchParams();

  // Handle Saved Filter separately if active
  if (currentQuickFilter === 'saved') {
    params.set('status_filter', 'all');
  } else if (currentTab === 'expired-events') {
    params.set('status_filter', 'expired');
  } else {
    // Default: strictly active & upcoming events
    params.set('status_filter', 'active');
  }

  if (selectedInterests.length > 0) {
    params.set('interests', selectedInterests.join(','));
  }
  if (currentDepartment !== 'All') {
    params.set('department', currentDepartment);
  }
  if (currentSearchQuery) {
    params.set('query', currentSearchQuery);
  }
  if (currentQuickFilter && currentQuickFilter !== 'saved') {
    params.set('quick_filter', currentQuickFilter);
  }

  // Tab-specific rules
  if (currentTab === 'live-updates') {
    params.set('only_email_updates', 'true');
  }

  try {
    const res = await fetch(`/api/events?${params.toString()}`);
    const data = await res.json();
    
    let events = data.events || [];

    // If 'saved' quick filter is clicked, filter by savedEventIds
    if (currentQuickFilter === 'saved') {
      events = events.filter(e => savedEventIds.includes(e.id));
    }

    allEventsCache = events;
    loading.classList.add('hidden');

    if (currentTab === 'recommended') {
      document.getElementById('tabBadge-recommended').textContent = events.length;
    }

    if (!events || events.length === 0) {
      empty.classList.remove('hidden');
      const titleElem = document.getElementById('emptyStateTitle');
      const descElem = document.getElementById('emptyStateDesc');
      if (currentTab === 'expired-events') {
        titleElem.textContent = "No past / expired events found";
        descElem.textContent = "All matching records are active or upcoming.";
      } else if (currentQuickFilter === 'saved') {
        titleElem.textContent = "You haven't bookmarked any events yet";
        descElem.textContent = "Click the star icon on any event card to save it here.";
      } else {
        titleElem.textContent = "No events matched your search or filters";
        descElem.textContent = "Try clearing the search query or switching tabs.";
      }
      return;
    }

    renderEventCards(events);
  } catch (err) {
    loading.classList.add('hidden');
    console.error("Error loading events:", err);
    empty.classList.remove('hidden');
  }
}

// Render Event Cards Grid
function renderEventCards(events) {
  const grid = document.getElementById('eventsGrid');
  grid.innerHTML = '';

  events.forEach(ev => {
    const card = document.createElement('div');
    card.className = "glass-card rounded-2xl p-5 flex flex-col justify-between border border-slate-200/90 hover:border-blue-300 transition-all bg-white relative overflow-hidden group";

    const isLiveUpdate = ev.has_email_update;
    const isStandalone = ev.is_standalone_email;
    const isExpired = ev.is_expired;
    const matchScore = ev.match_score || 0;
    const isSaved = savedEventIds.includes(ev.id);

    // Dynamic Countdown Badge
    let countdownBadge = "";
    if (isExpired) {
      countdownBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200"><i class="fa-solid fa-flag-checkered mr-1"></i>${ev.countdown_text || 'Completed'}</span>`;
    } else if (ev.status === 'Happening Today!') {
      countdownBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-100 text-rose-800 border border-rose-300 flex items-center space-x-1"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 pulse-badge inline-block mr-1"></span>🔥 Today</span>`;
    } else if (ev.status === 'Tomorrow') {
      countdownBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">⚡ Tomorrow</span>`;
    } else {
      countdownBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200"><i class="fa-regular fa-clock mr-1"></i>${ev.countdown_text || 'Upcoming'}</span>`;
    }

    // Color code match score
    let scoreColor = "bg-blue-50 text-blue-700 border-blue-200";
    if (matchScore >= 50) scoreColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
    else if (matchScore >= 30) scoreColor = "bg-amber-50 text-amber-700 border-amber-200";

    // Venue badge style
    const venueText = ev.venue || 'Campus';
    const isEnrichedVenue = isLiveUpdate && ev.venue && ev.venue !== 'Campus' && ev.venue !== 'N/A';
    const venueClass = isEnrichedVenue ? 'bg-emerald-100/90 text-emerald-900 font-bold border-emerald-300' : 'bg-slate-100 text-slate-700 border-slate-200';

    // Registration link
    const regLink = ev.registration_link || (ev.email_data && ev.email_data.registration_link);
    const whatsappLink = ev.whatsapp_link || (ev.email_data && ev.email_data.whatsapp_link);

    card.innerHTML = `
      <div>
        <!-- Top Tags Row -->
        <div class="flex items-center justify-between gap-2 mb-2.5">
          <div class="flex items-center space-x-1.5 flex-wrap gap-y-1">
            ${countdownBadge}
            <span class="text-[11px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
              <i class="fa-regular fa-building text-[10px] mr-1 text-slate-500"></i>${ev.department || 'General'}
            </span>
            ${isStandalone ? `
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-100 text-purple-900 border border-purple-300 flex items-center space-x-1">
                <i class="fa-solid fa-bullhorn text-[9px] mr-1"></i><span>New Notice</span>
              </span>
            ` : isLiveUpdate ? `
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-amber-100 text-amber-900 border border-amber-300">
                ⚡ Email Update
              </span>
            ` : ''}
          </div>

          <!-- Bookmark Star Icon Button -->
          <button onclick="toggleBookmark('${ev.id}')" title="${isSaved ? 'Remove Bookmark' : 'Save Event'}" class="text-sm p-1 transition ${isSaved ? 'text-amber-500 hover:text-amber-600' : 'text-slate-300 hover:text-amber-400'}">
            <i class="${isSaved ? 'fa-solid' : 'fa-regular'} fa-star"></i>
          </button>
        </div>

        <!-- Event Title -->
        <h3 class="text-base font-bold text-slate-900 leading-snug line-clamp-2 group-hover:text-blue-600 transition font-heading mb-1.5">
          ${ev.title}
        </h3>

        <!-- Match Score and Reason -->
        <div class="flex items-center space-x-2 mb-3">
          <span class="text-xs font-extrabold px-2 py-0.5 rounded-full border ${scoreColor} shadow-sm shrink-0">
            ${matchScore}% Match
          </span>
          <span class="text-[11px] text-blue-700 bg-blue-50/70 border border-blue-100 px-2 py-0.5 rounded-lg line-clamp-1">
            ${ev.why_recommended || 'Recommended'}
          </span>
        </div>

        <!-- Metadata Badges -->
        <div class="space-y-1.5 text-xs bg-slate-50/80 p-3 rounded-xl border border-slate-100">
          <!-- Date -->
          <div class="flex items-center text-slate-700">
            <div class="w-5 text-slate-400"><i class="fa-regular fa-calendar"></i></div>
            <span class="font-medium">${ev.start_date || 'TBD'} ${ev.day ? '(' + ev.day + ')' : ''}</span>
          </div>

          <!-- Venue -->
          <div class="flex items-center">
            <div class="w-5 text-slate-400"><i class="fa-solid fa-location-dot"></i></div>
            <span class="px-2 py-0.5 rounded-md border text-[11px] ${venueClass} line-clamp-1">
              📍 ${venueText}
            </span>
          </div>

          <!-- Time -->
          ${ev.time && ev.time !== 'TBD' ? `
            <div class="flex items-center text-slate-600">
              <div class="w-5 text-slate-400"><i class="fa-regular fa-clock"></i></div>
              <span class="text-[11px] font-medium text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">⏰ ${ev.time}</span>
            </div>
          ` : ''}

          <!-- Deadline if present -->
          ${ev.deadline ? `
            <div class="flex items-center text-rose-700 font-semibold">
              <div class="w-5 text-rose-500"><i class="fa-regular fa-bell"></i></div>
              <span class="text-[11px]">Deadline: ${ev.deadline}</span>
            </div>
          ` : ''}

          <!-- Stall info if present -->
          ${ev.stall_info ? `
            <div class="flex items-center text-amber-800 font-semibold">
              <div class="w-5 text-amber-500"><i class="fa-solid fa-store"></i></div>
              <span class="text-[11px] bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">${ev.stall_info}</span>
            </div>
          ` : ''}
        </div>
      </div>

      <!-- Action Footer -->
      <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 flex-wrap">
        
        <div class="flex items-center space-x-1.5">
          <button onclick="openEventModal('${ev.id}')" class="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center space-x-1 py-1.5 px-2.5 rounded-lg hover:bg-blue-50 transition border border-transparent hover:border-blue-100">
            <i class="fa-regular fa-eye"></i>
            <span>Details</span>
          </button>

          <!-- Direct Register Form Button -->
          ${regLink ? `
            <a href="${regLink}" target="_blank" rel="noopener" class="text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 py-1.5 px-2.5 rounded-lg flex items-center space-x-1 transition shadow-sm">
              <i class="fa-solid fa-file-pen text-[10px]"></i>
              <span>Register</span>
            </a>
          ` : ''}

          <!-- Direct WhatsApp Button -->
          ${whatsappLink ? `
            <a href="${whatsappLink}" target="_blank" rel="noopener" class="text-xs font-bold text-emerald-800 bg-emerald-100 hover:bg-emerald-200 border border-emerald-300 p-1.5 rounded-lg flex items-center justify-center transition" title="Join WhatsApp Group">
              <i class="fa-brands fa-whatsapp text-sm"></i>
            </a>
          ` : ''}
        </div>

        <div class="flex items-center space-x-1.5">
          <!-- Share via WhatsApp / Copy -->
          <button onclick="shareEvent('${ev.id}')" title="Share event details" class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 flex items-center justify-center transition border border-slate-200 text-xs">
            <i class="fa-solid fa-share-nodes"></i>
          </button>

          <!-- Add to Google Calendar -->
          <a href="${getGoogleCalendarUrl(ev)}" target="_blank" rel="noopener" title="Add to Google Calendar" class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-blue-50 hover:text-blue-600 text-slate-600 flex items-center justify-center transition border border-slate-200 text-xs">
            <i class="fa-brands fa-google"></i>
          </a>

          <!-- Download .ics -->
          <a href="/api/export_ics/${ev.id}" download title="Download iCal file" class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-amber-50 hover:text-amber-700 text-slate-600 flex items-center justify-center transition border border-slate-200 text-xs">
            <i class="fa-solid fa-arrow-down-to-bracket"></i>
          </a>
        </div>

      </div>
    `;

    grid.appendChild(card);
  });
}

// Tab Switching
function switchTab(tabId) {
  currentTab = tabId;

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('border-blue-600', 'text-blue-600', 'active-tab');
    btn.classList.add('border-transparent', 'text-slate-500');
  });
  const activeBtn = document.getElementById(`tabBtn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.remove('border-transparent', 'text-slate-500');
    activeBtn.classList.add('border-blue-600', 'text-blue-600', 'active-tab');
  }

  const eventsSection = document.getElementById('eventsSection');
  const filterControls = document.getElementById('filterControls');
  const quickFilters = document.getElementById('quickFilterPills');
  const interestsSection = document.getElementById('interestsSection');
  const nlpSection = document.getElementById('nlpInspectorSection');

  if (tabId === 'nlp-inspector') {
    eventsSection.classList.add('hidden');
    filterControls.classList.add('hidden');
    quickFilters.classList.add('hidden');
    nlpSection.classList.remove('hidden');
    loadNlpEmails();
  } else {
    eventsSection.classList.remove('hidden');
    filterControls.classList.remove('hidden');
    quickFilters.classList.remove('hidden');
    nlpSection.classList.add('hidden');

    if (tabId === 'expired-events') {
      interestsSection.classList.add('hidden');
    } else {
      interestsSection.classList.remove('hidden');
    }

    loadEvents();
  }
}

// Quick Filter Handling (Today, This Week, Registration, Saved)
function setQuickFilter(qf) {
  currentQuickFilter = qf;

  document.querySelectorAll('.qf-btn').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
    btn.classList.add('bg-slate-100', 'text-slate-700');
  });

  const activeBtn = document.getElementById(`qf-${qf || 'all'}`);
  if (activeBtn) {
    activeBtn.classList.remove('bg-slate-100', 'text-slate-700');
    activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
  }

  loadEvents();
}

// Bookmarking / Saved Events
function toggleBookmark(eventId) {
  if (savedEventIds.includes(eventId)) {
    savedEventIds = savedEventIds.filter(id => id !== eventId);
    showToast("Event removed from bookmarks");
  } else {
    savedEventIds.push(eventId);
    showToast("Event saved to bookmarks ⭐");
  }
  localStorage.setItem('caias_saved_events', JSON.stringify(savedEventIds));
  updateSavedBadge();
  loadEvents();
}

function updateSavedBadge() {
  const badge = document.getElementById('savedCountBadge');
  if (badge) badge.textContent = savedEventIds.length;
}

// Share Event Details
function shareEvent(eventId) {
  const ev = allEventsCache.find(e => e.id === eventId);
  if (!ev) return;

  const regLink = ev.registration_link || (ev.email_data && ev.email_data.registration_link) || '';
  const text = `🎓 *${ev.title}*\n📍 Venue: ${ev.venue || 'Campus'}\n📅 Date: ${ev.start_date}\n⏰ Time: ${ev.time || 'Refer to notice'}\n${regLink ? '📝 Register: ' + regLink + '\n' : ''}Shared from CAIAS AI Event Assistant`;

  if (navigator.share) {
    navigator.share({
      title: ev.title,
      text: text
    }).catch(() => copyToClipboard(text));
  } else {
    copyToClipboard(text);
  }
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Event summary copied to clipboard! 📋");
  }).catch(() => {
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
  });
}

function showToast(msg) {
  const toast = document.getElementById('toastNotification');
  const textElem = document.getElementById('toastMessage');
  textElem.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 2500);
}

// Load NLP Email Inspector Tab
async function loadNlpEmails() {
  const container = document.getElementById('nlpEmailList');
  container.innerHTML = `
    <div class="py-12 text-center text-slate-400">
      <i class="fa-solid fa-spinner animate-spin text-2xl mb-2 text-blue-500"></i>
      <p class="text-xs">Fetching and analyzing recent emails...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/email_notices');
    const data = await res.json();
    allEmailsCache = data.emails || [];

    if (!data.emails || data.emails.length === 0) {
      container.innerHTML = `
        <div class="py-12 text-center text-slate-400">
          <p class="text-sm">No recent emails found or synced yet.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = '';
    data.emails.forEach(item => {
      const emailCard = document.createElement('div');
      emailCard.className = `p-4 rounded-xl border ${item.is_event ? 'border-amber-300 bg-amber-50/30' : 'border-slate-200 bg-slate-50'} transition`;

      const confBadge = item.is_event 
        ? `<span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
            <i class="fa-solid fa-bolt mr-1"></i>Event Notice (${item.confidence_score}% Confidence)
          </span>`
        : `<span class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-200 text-slate-600">
            Administrative / General Mail
          </span>`;

      emailCard.innerHTML = `
        <div class="flex items-start justify-between gap-3 mb-2">
          <div>
            <div class="flex items-center space-x-2 flex-wrap gap-y-1 mb-1">
              ${confBadge}
              <span class="text-xs font-semibold text-slate-700">${item.email_sender || 'Unknown Sender'}</span>
              <span class="text-[11px] text-slate-400">• ${item.email_date || ''}</span>
            </div>
            <h4 class="text-sm font-bold text-slate-900">${item.email_subject || '(No Subject)'}</h4>
          </div>
        </div>

        <p class="text-xs text-slate-600 line-clamp-2 bg-white/80 p-2.5 rounded-lg border border-slate-200/70 mb-3">
          ${item.snippet || 'No snippet preview'}
        </p>

        <!-- Extracted NLP Entities Badges -->
        <div class="flex items-center flex-wrap gap-2 text-[11px]">
          <span class="font-bold text-slate-500 uppercase tracking-wider text-[10px]">Extracted NLP Entities:</span>
          
          <span class="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold border border-blue-200 flex items-center space-x-1">
            <i class="fa-solid fa-location-dot text-[10px]"></i>
            <span>Venue: ${item.venue}</span>
          </span>

          <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold border border-emerald-200 flex items-center space-x-1">
            <i class="fa-regular fa-calendar text-[10px]"></i>
            <span>Date: ${item.formatted_date}</span>
          </span>

          <span class="px-2 py-0.5 rounded bg-purple-100 text-purple-800 font-semibold border border-purple-200 flex items-center space-x-1">
            <i class="fa-regular fa-clock text-[10px]"></i>
            <span>Time: ${item.time}</span>
          </span>

          ${item.registration_link ? `
            <a href="${item.registration_link}" target="_blank" class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-300 flex items-center space-x-1 hover:underline">
              <i class="fa-solid fa-file-pen text-[10px]"></i>
              <span>Registration Form</span>
            </a>
          ` : ''}

          ${item.whatsapp_link ? `
            <a href="${item.whatsapp_link}" target="_blank" class="px-2 py-0.5 rounded bg-green-100 text-green-800 font-bold border border-green-300 flex items-center space-x-1 hover:underline">
              <i class="fa-brands fa-whatsapp text-[10px]"></i>
              <span>WhatsApp Group</span>
            </a>
          ` : ''}

          ${item.stall_info ? `
            <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold border border-amber-300">
              🏪 ${item.stall_info}
            </span>
          ` : ''}

          ${item.deadline ? `
            <span class="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-semibold border border-rose-300">
              ⏰ Deadline: ${item.deadline}
            </span>
          ` : ''}
        </div>
      `;

      container.appendChild(emailCard);
    });

  } catch (err) {
    container.innerHTML = `<div class="p-4 text-xs text-red-600">Error loading emails: ${err.message}</div>`;
  }
}

// Trigger Live Gmail Sync (Refreshes tokens & polls)
async function triggerEmailSync() {
  const icon = document.getElementById('syncIcon');
  const text = document.getElementById('syncText');
  const btn = document.getElementById('syncBtn');

  icon.classList.add('animate-spin');
  text.textContent = 'Syncing...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/sync_emails?max_count=35', { method: 'POST' });
    const data = await res.json();
    
    showToast("Gmail synced & tokens verified! 🔄");
    nextSyncRemainingSeconds = 1800;
    await fetchAppStatus();

    if (currentTab === 'nlp-inspector') {
      await loadNlpEmails();
    } else {
      await loadEvents();
    }
  } catch (err) {
    alert("Could not sync emails: " + err.message);
  } finally {
    icon.classList.remove('animate-spin');
    text.textContent = 'Sync Now';
    btn.disabled = false;
  }
}

// Search & Filter Helpers
function debounceSearch() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    currentSearchQuery = document.getElementById('searchInput').value.trim();
    loadEvents();
  }, 300);
}

function applyFilters() {
  currentDepartment = document.getElementById('departmentSelect').value;
  loadEvents();
}

function toggleInterest(interest) {
  if (selectedInterests.includes(interest)) {
    selectedInterests = selectedInterests.filter(i => i !== interest);
  } else {
    selectedInterests.push(interest);
  }
  updateInterestPillStyles();
  loadEvents();
}

function resetInterests() {
  selectedInterests = ['Coding and Programming', 'Artificial Intelligence', 'Business and Entrepreneurship'];
  updateInterestPillStyles();
  loadEvents();
}

function resetFilters() {
  document.getElementById('searchInput').value = '';
  currentSearchQuery = '';
  document.getElementById('departmentSelect').value = 'All';
  currentDepartment = 'All';
  setQuickFilter('');
  resetInterests();
}

function updateInterestPillStyles() {
  document.querySelectorAll('.interest-pill').forEach(btn => {
    const val = btn.getAttribute('data-interest');
    if (selectedInterests.includes(val)) {
      btn.className = "interest-pill text-xs px-2.5 py-1 rounded-lg border border-blue-500 bg-blue-600 text-white font-semibold shadow-sm transition cursor-pointer";
    } else {
      btn.className = "interest-pill text-xs px-2.5 py-1 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 font-medium transition cursor-pointer";
    }
  });
}

// Event Details Modal (With Deep Metadata)
function openEventModal(eventId) {
  const ev = allEventsCache.find(e => e.id === eventId);
  if (!ev) return;

  const modal = document.getElementById('eventModal');
  const content = document.getElementById('modalContent');

  const isLiveUpdate = ev.has_email_update;
  const isStandalone = ev.is_standalone_email;
  const isExpired = ev.is_expired;
  const emailData = ev.email_data;

  const regLink = ev.registration_link || (emailData && emailData.registration_link);
  const whatsappLink = ev.whatsapp_link || (emailData && emailData.whatsapp_link);
  const deadline = ev.deadline || (emailData && emailData.deadline);
  const eligibility = ev.eligibility || (emailData && emailData.eligibility);
  const contacts = ev.contact_numbers || (emailData && emailData.contact_numbers) || [];
  const highlights = ev.highlights || (emailData && emailData.highlights) || [];
  const stallInfo = ev.stall_info || (emailData && emailData.stall_info);

  content.innerHTML = `
    <!-- Modal Header -->
    <div class="mb-4">
      <div class="flex items-center space-x-2 mb-2 flex-wrap gap-y-1">
        <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-slate-100 text-slate-800 border border-slate-200">
          <i class="fa-regular fa-building mr-1"></i>${ev.department || 'General'}
        </span>
        
        ${isExpired ? `
          <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 border border-slate-300">
            <i class="fa-solid fa-flag-checkered mr-1"></i>${ev.countdown_text || 'Completed'}
          </span>
        ` : `
          <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-blue-100 text-blue-800 border border-blue-200">
            ${ev.countdown_text || 'Upcoming'}
          </span>
        `}

        ${isStandalone ? `
          <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-purple-100 text-purple-900 border border-purple-300">
            📢 Live Email Notice
          </span>
        ` : isLiveUpdate ? `
          <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-100 text-amber-900 border border-amber-300">
            ⚡ Email Confirmed
          </span>
        ` : `
          <span class="text-xs font-medium px-2 py-0.5 rounded bg-slate-50 text-slate-500 border border-slate-200">
            Page ${ev.source_page} in Calendar
          </span>
        `}
      </div>

      <h2 class="text-xl font-bold text-slate-900 font-heading leading-snug">${ev.title}</h2>
    </div>

    <!-- Metadata Details Grid -->
    <div class="grid grid-cols-2 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200/80 text-xs mb-4">
      <div>
        <span class="text-slate-400 block font-medium mb-0.5">Start Date</span>
        <span class="font-bold text-slate-800">${ev.start_date || 'N/A'} ${ev.day ? '(' + ev.day + ')' : ''}</span>
      </div>
      <div>
        <span class="text-slate-400 block font-medium mb-0.5">End Date</span>
        <span class="font-bold text-slate-800">${ev.end_date || ev.start_date || 'N/A'}</span>
      </div>
      <div>
        <span class="text-slate-400 block font-medium mb-0.5">Venue / Location</span>
        <span class="font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 inline-block">
          📍 ${ev.venue || 'Campus / TBA'}
        </span>
      </div>
      <div>
        <span class="text-slate-400 block font-medium mb-0.5">Time</span>
        <span class="font-bold text-slate-800">⏰ ${ev.time || 'Refer to notice'}</span>
      </div>
    </div>

    <!-- Additional Extracted Metadata Badges -->
    ${(regLink || whatsappLink || deadline || eligibility || stallInfo || contacts.length > 0) ? `
      <div class="p-3.5 bg-blue-50/50 rounded-xl border border-blue-200/80 text-xs mb-4 space-y-2">
        <div class="font-bold text-blue-900 flex items-center space-x-1.5">
          <i class="fa-solid fa-circle-info text-blue-600"></i>
          <span>Event Highlights & Participation Info:</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
          ${deadline ? `
            <div class="bg-white p-2 rounded-lg border border-blue-100">
              <strong class="text-rose-700 block">⏰ Registration Deadline:</strong>
              <span class="text-slate-700">${deadline}</span>
            </div>
          ` : ''}

          ${eligibility ? `
            <div class="bg-white p-2 rounded-lg border border-blue-100">
              <strong class="text-blue-800 block">👥 Target Audience:</strong>
              <span class="text-slate-700">${eligibility}</span>
            </div>
          ` : ''}

          ${stallInfo ? `
            <div class="bg-white p-2 rounded-lg border border-amber-200">
              <strong class="text-amber-800 block">🏪 Stall Information:</strong>
              <span class="text-slate-700">${stallInfo}</span>
            </div>
          ` : ''}

          ${contacts.length > 0 ? `
            <div class="bg-white p-2 rounded-lg border border-blue-100">
              <strong class="text-slate-700 block">📞 Contact Numbers:</strong>
              <span class="text-slate-700">${contacts.join(', ')}</span>
            </div>
          ` : ''}
        </div>

        ${highlights.length > 0 ? `
          <div class="bg-white p-2.5 rounded-lg border border-blue-100 mt-2">
            <strong class="text-slate-800 block mb-1">✨ Key Highlights / Features:</strong>
            <ul class="list-disc list-inside text-slate-600 text-[11px] space-y-0.5">
              ${highlights.map(h => `<li>${h}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    ` : ''}

    <!-- Live Email Information Section -->
    ${isLiveUpdate && emailData ? `
      <div class="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200 mb-4 text-xs">
        <div class="flex items-center space-x-2 font-bold text-amber-900 mb-1.5">
          <i class="fa-solid fa-envelope-open-text text-amber-600"></i>
          <span>Correlated Live Gmail Announcement:</span>
        </div>
        <div class="space-y-1 text-slate-700">
          <div><strong>Subject:</strong> ${emailData.subject || ''}</div>
          <div><strong>Sender:</strong> ${emailData.sender || ''}</div>
          <div><strong>Date Received:</strong> ${emailData.date || ''}</div>
          <div class="mt-2 pt-2 border-t border-amber-200/60 text-slate-600 italic bg-white/70 p-2.5 rounded-lg border border-amber-100 text-[11px]">
            "${emailData.snippet || 'No snippet preview'}"
          </div>
        </div>
      </div>
    ` : ''}

    <!-- Modal Footer Actions -->
    <div class="flex items-center justify-between pt-3 border-t border-slate-100 flex-wrap gap-2">
      <div class="flex items-center space-x-2">
        ${regLink ? `
          <a href="${regLink}" target="_blank" rel="noopener" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm transition flex items-center space-x-1.5">
            <i class="fa-solid fa-file-pen"></i>
            <span>Open Registration Form</span>
          </a>
        ` : ''}

        ${whatsappLink ? `
          <a href="${whatsappLink}" target="_blank" rel="noopener" class="px-3 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-900 text-xs font-bold rounded-xl border border-emerald-300 transition flex items-center space-x-1.5">
            <i class="fa-brands fa-whatsapp text-sm text-emerald-600"></i>
            <span>Join WhatsApp</span>
          </a>
        ` : ''}
      </div>

      <div class="flex items-center space-x-2">
        <button onclick="shareEvent('${ev.id}')" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl border border-slate-300 transition flex items-center space-x-1.5">
          <i class="fa-solid fa-share-nodes"></i>
          <span>Share</span>
        </button>

        <a href="${getGoogleCalendarUrl(ev)}" target="_blank" rel="noopener" class="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-sm transition flex items-center space-x-1.5">
          <i class="fa-brands fa-google"></i>
          <span>Google Calendar</span>
        </a>

        <a href="/api/export_ics/${ev.id}" download class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl border border-slate-300 transition flex items-center space-x-1">
          <i class="fa-solid fa-file-arrow-down"></i>
          <span>.ics</span>
        </a>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeModal() {
  document.getElementById('eventModal').classList.add('hidden');
}

// Generate Google Calendar Web URL
function getGoogleCalendarUrl(ev) {
  const base = "https://calendar.google.com/calendar/render?action=TEMPLATE";
  const title = encodeURIComponent(ev.title || "CAIAS Event");
  const venue = encodeURIComponent(ev.venue || "CAIAS Campus");
  
  let startFormatted = (ev.start_date || "").replace(/-/g, '');
  let endFormatted = (ev.end_date || ev.start_date || "").replace(/-/g, '');

  if (!startFormatted || startFormatted.length !== 8) {
    const now = new Date();
    startFormatted = now.toISOString().slice(0, 10).replace(/-/g, '');
    endFormatted = startFormatted;
  }

  const datesParam = `${startFormatted}/${endFormatted}`;
  let details = `Department: ${ev.department || 'CAIAS'}\nVenue: ${ev.venue || 'Campus'}\nTime: ${ev.time || 'TBD'}`;
  
  const regLink = ev.registration_link || (ev.email_data && ev.email_data.registration_link);
  if (regLink) {
    details += `\nRegistration Form: ${regLink}`;
  }
  if (ev.email_data) {
    details += `\n\nEmail Notice: ${ev.email_data.subject}\nSnippet: ${ev.email_data.snippet}`;
  }

  return `${base}&text=${title}&dates=${datesParam}&details=${encodeURIComponent(details)}&location=${venue}`;
}
