import { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE =
  import.meta.env.VITE_API_URL ||
  (window.location.origin.includes("localhost:5173")
    ? "http://localhost:8000"
    : window.location.origin);

// ── Icons ──────────────────────────────────────────────────────────
const FacebookIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c4.56-.93 8-4.96 8-9.75z"/>
  </svg>
);

const InstagramIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
  </svg>
);

const LinkedInIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const CrossIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

const UploadIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
);

const ExternalLinkIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
    <polyline points="15 3 21 3 21 9"/>
    <line x1="10" y1="14" x2="21" y2="3"/>
  </svg>
);

function App() {
  const [config, setConfig] = useState(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [caption, setCaption] = useState("");
  
  // Platform settings
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  
  // Image options
  const [imageSource, setImageSource] = useState("file"); // "file" or "url"
  const [imageFile, setImageFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [imageUrl, setImageUrl] = useState("");

  // UI state
  const [activePreviewTab, setActivePreviewTab] = useState("facebook");
  const [isPosting, setIsPosting] = useState(false);
  const [postResult, setPostResult] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoadingConfig(true);
      const res = await fetch(`${API_BASE}/api/config`);
      const data = await res.json();
      setConfig(data);
      
      // Auto-select all connected platforms
      const connected = [];
      if (data?.status?.facebook) connected.push("facebook");
      if (data?.status?.instagram) connected.push("instagram");
      if (data?.status?.linkedin) connected.push("linkedin");
      setSelectedPlatforms(connected);
      
      // Default preview tab to first connected platform
      if (connected.length > 0) {
        setActivePreviewTab(connected[0]);
      }
    } catch (err) {
      console.error(err);
      addToast("Failed to connect to backend API.", "error");
    } finally {
      setLoadingConfig(false);
    }
  };

  const addToast = (message, type = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        addToast("Please upload a valid image file.", "error");
        return;
      }
      setImageFile(file);
      setImagePreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        addToast("Please upload a valid image file.", "error");
        return;
      }
      setImageFile(file);
      setImagePreviewUrl(URL.createObjectURL(file));
    }
  };

  const removeSelectedFile = () => {
    setImageFile(null);
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
      setImagePreviewUrl("");
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const togglePlatform = (platform) => {
    if (!config?.status?.[platform]) return; // Cannot toggle if not configured
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (selectedPlatforms.length === 0) {
      addToast("At least one platform must be selected.", "error");
      return;
    }
    if (!caption.trim()) {
      addToast("Post caption is required.", "error");
      return;
    }

    setIsPosting(true);
    setPostResult(null);

    const formData = new FormData();
    formData.append("caption", caption);
    formData.append("platforms", JSON.stringify(selectedPlatforms));

    if (imageSource === "file" && imageFile) {
      formData.append("image", imageFile);
    } else if (imageSource === "url" && imageUrl.trim()) {
      formData.append("image_url", imageUrl.trim());
    }

    try {
      const res = await fetch(`${API_BASE}/api/post`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        setPostResult(data);
        if (data.success) {
          addToast("Successfully posted to all channels!", "success");
        } else {
          addToast("Posting failed on some platforms.", "error");
        }
      } else {
        const errMsg = data.detail?.message || data.detail || "Failed to submit post.";
        addToast(errMsg, "error");
      }
    } catch (err) {
      console.error(err);
      addToast("API error. Ensure your backend is running.", "error");
    } finally {
      setIsPosting(false);
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case "facebook": return <FacebookIcon />;
      case "instagram": return <InstagramIcon />;
      case "linkedin": return <LinkedInIcon />;
      default: return null;
    }
  };

  const resetForm = () => {
    setCaption("");
    removeSelectedFile();
    setImageUrl("");
    setPostResult(null);
  };

  // Get active preview image
  const getPreviewImage = () => {
    if (imageSource === "file") {
      return imagePreviewUrl;
    }
    return imageUrl.trim();
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-title-container">
          <span className="app-logo">🚀</span>
          <h1 className="app-title">One-Click Social Poster</h1>
        </div>
        <p className="app-subtitle">Publish updates automatically to Facebook, Instagram, and LinkedIn in one click.</p>
      </header>

      {/* Main Dashboard Grid */}
      <div className="dashboard-grid">
        {postResult ? (
          /* Results View */
          <div className="results-card glass-panel">
            <div className="results-header-status">
              <div className={`results-badge-main ${postResult.success ? 'success' : 'failure'}`}>
                {postResult.success ? <CheckIcon /> : <CrossIcon />}
              </div>
              <h2>{postResult.success ? 'Post Published Successfully!' : 'Failed to Publish'}</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                Review details for each channel below.
              </p>
            </div>

            <div className="results-list">
              {postResult.results.map((r, idx) => (
                <div key={idx} className="result-row">
                  <div className="result-platform-info">
                    <span className={`result-status-icon ${r.success ? 'success' : 'error'}`}>
                      {r.success ? <CheckIcon /> : <CrossIcon />}
                    </span>
                    <span className={`${r.platform.toLowerCase()}-icon-wrap`}>
                      {getPlatformIcon(r.platform.toLowerCase())}
                    </span>
                    <span style={{ fontWeight: '600' }}>{r.platform}</span>
                  </div>
                  
                  <div>
                    {r.success ? (
                      r.url ? (
                        <a href={r.url} target="_blank" rel="noopener noreferrer" className="result-link">
                          View Post <ExternalLinkIcon />
                        </a>
                      ) : (
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Success</span>
                      )
                    ) : (
                      <span className="result-error-msg" title={r.error}>
                        {r.error || "Unknown Error"}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <button type="button" className="reset-btn" onClick={resetForm}>
              Create Another Post
            </button>
          </div>
        ) : (
          /* Creator Form */
          <form className="creator-card glass-panel" onSubmit={handleSubmit}>
            {/* Platform Selection */}
            <div className="form-group">
              <label className="form-label">Target Channels <span style={{fontSize: '0.8rem', fontWeight: 'normal', color: 'var(--text-muted)'}}>(select channels to publish to)</span></label>
              <div className="platform-selector-grid">
                {["facebook", "instagram", "linkedin"].map((platform) => {
                  const isConnected = config?.status?.[platform];
                  const isSelected = selectedPlatforms.includes(platform);
                  
                  return (
                    <label 
                      key={platform} 
                      className={`platform-checkbox-label ${isSelected ? 'selected' : ''} ${!isConnected ? 'disabled' : ''}`}
                      onClick={() => togglePlatform(platform)}
                    >
                      <input 
                        type="checkbox" 
                        className="hidden-checkbox"
                        checked={isSelected}
                        disabled={!isConnected}
                        onChange={() => {}} // handled by click
                      />
                      <span className={`${platform}-icon-wrap`}>
                        {getPlatformIcon(platform)}
                      </span>
                      <span style={{ fontSize: "0.85rem", fontWeight: "600" }}>
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Post Caption */}
            <div className="form-group">
              <div className="form-label">
                <span>Post Caption</span>
                <span className="char-counter">{caption.length} characters</span>
              </div>
              <textarea
                className="form-textarea"
                placeholder="Share something interesting! Include hashtags like #product #update..."
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                required
              />
            </div>

            {/* Attachment options */}
            <div className="form-group">
              <label className="form-label">Attach Image</label>
              
              <div className="tabs-container" style={{ marginBottom: "12px" }}>
                <button 
                  type="button" 
                  className={`tab-btn ${imageSource === "file" ? "active" : ""}`}
                  onClick={() => setImageSource("file")}
                >
                  Local Upload
                </button>
                <button 
                  type="button" 
                  className={`tab-btn ${imageSource === "url" ? "active" : ""}`}
                  onClick={() => setImageSource("url")}
                >
                  Image URL
                </button>
              </div>

              {imageSource === "file" ? (
                /* File Upload Zone */
                imageFile ? (
                  <div className="image-preview-container">
                    <img src={imagePreviewUrl} alt="Upload preview" className="preview-thumbnail" />
                    <div className="preview-meta">
                      <div className="preview-filename">{imageFile.name}</div>
                      <div className="preview-filesize">{(imageFile.size / (1024 * 1024)).toFixed(2)} MB</div>
                    </div>
                    <button type="button" className="remove-image-btn" onClick={removeSelectedFile}>
                      <TrashIcon />
                    </button>
                  </div>
                ) : (
                  <div
                    className={`drag-drop-zone ${isDragging ? 'dragging' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      className="file-input-hidden"
                      accept="image/jpeg,image/png,image/gif"
                      onChange={handleFileChange}
                    />
                    <span className="upload-icon"><UploadIcon /></span>
                    <span className="upload-prompt">Drag & Drop image here</span>
                    <span className="upload-subprompt">Supports JPG, PNG, GIF (Max 8-10MB)</span>
                  </div>
                )
              ) : (
                /* Image URL Input */
                <div className="url-input-container">
                  <input
                    type="url"
                    className="url-input"
                    placeholder="https://example.com/image.jpg"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                  />
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="submit-btn"
              disabled={isPosting || !caption.trim()}
            >
              {isPosting ? (
                <>
                  <span className="spinner"></span>
                  Publishing to selected channels...
                </>
              ) : (
                <>🚀 Publish Update Now</>
              )}
            </button>
          </form>
        )}

        {/* Live Social Preview Mockup */}
        <div className="preview-card glass-panel">
          <h2 className="section-title" style={{ fontSize: "1rem", color: "var(--text-secondary)" }}>
            <span>👁️</span> Live Post Preview
          </h2>

          <div className="preview-tabs">
            {["facebook", "instagram", "linkedin"].map((platform) => {
              const isActive = activePreviewTab === platform;
              return (
                <button
                  type="button"
                  key={platform}
                  className={`preview-tab ${platform}-tab ${isActive ? "active" : ""}`}
                  onClick={() => setActivePreviewTab(platform)}
                >
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </button>
              );
            })}
          </div>

          <div className="phone-mockup">
            <div className="mockup-header">
              <div className="mockup-avatar">
                {activePreviewTab.charAt(0).toUpperCase()}
              </div>
              <div className="mockup-meta">
                <span className="mockup-author">My Brand Account</span>
                <span className="mockup-time">Just now • 🌍</span>
              </div>
            </div>

            <div className={`mockup-content ${!caption ? "empty" : ""}`}>
              {caption || "Your post description will show up here. Add text in the editor to preview..."}
            </div>

            <div className="mockup-media-container">
              {getPreviewImage() ? (
                <img 
                  src={getPreviewImage()} 
                  alt="Post preview" 
                  className="mockup-media"
                  onError={(e) => {
                    // Fallback if URL is invalid/broken
                    e.target.style.display = "none";
                  }}
                />
              ) : (
                <div className="mockup-media-placeholder">
                  <span className="mockup-placeholder-icon">📸</span>
                  <span>No Image Selected</span>
                </div>
              )}
            </div>

            <div className="mockup-footer">
              <div className="mockup-action">
                <span>👍</span>
                <span>Like</span>
              </div>
              <div className="mockup-action">
                <span>💬</span>
                <span>Comment</span>
              </div>
              <div className="mockup-action">
                <span>↩️</span>
                <span>Share</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Toasts */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            <span>
              {t.type === "success" ? "✅" : t.type === "error" ? "❌" : "⚠️"}
            </span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
