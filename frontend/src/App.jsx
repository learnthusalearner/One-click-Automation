import { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE =
  import.meta.env.VITE_API_URL ||
  (window.location.origin.includes("localhost:5173")
    ? "http://localhost:8000"
    : window.location.origin);

// ── Icons ──────────────────────────────────────────────────────────
const FacebookIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c4.56-.93 8-4.96 8-9.75z"/>
  </svg>
);

const InstagramIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
  </svg>
);

const LinkedInIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
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
  const [imageFile, setImageFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Find all configured platforms
    const activePlatforms = [];
    if (config?.status?.facebook) activePlatforms.push("facebook");
    if (config?.status?.instagram) activePlatforms.push("instagram");
    if (config?.status?.linkedin) activePlatforms.push("linkedin");

    if (activePlatforms.length === 0) {
      addToast("No connected social channels configured. Check .env file.", "error");
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
    formData.append("platforms", JSON.stringify(activePlatforms));

    if (imageFile) {
      formData.append("image", imageFile);
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
    setPostResult(null);
  };

  return (
    <div className="app-container" style={{maxWidth: '600px', padding: '30px 16px'}}>
      {/* Header */}
      <header className="app-header" style={{marginBottom: '20px'}}>
        <h1 className="app-title" style={{fontSize: '1.8rem'}}>One-Click Social Poster</h1>
        <p className="app-subtitle" style={{fontSize: '0.9rem'}}>Publish updates automatically to Facebook, Instagram, and LinkedIn in one click.</p>
      </header>

      {/* Connected Channels status header bar */}
      <div className="glass-panel" style={{padding: '12px 20px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px'}}>
        <span style={{fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)'}}>Active Channels:</span>
        <div style={{display: 'flex', gap: '12px'}}>
          {loadingConfig ? (
            <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Syncing...</span>
          ) : (
            ["facebook", "instagram", "linkedin"].map((platform) => {
              const isConnected = config?.status?.[platform];
              return (
                <div key={platform} style={{display: 'flex', alignItems: 'center', gap: '6px', opacity: isConnected ? 1 : 0.25}} title={`${platform}: ${isConnected ? 'Connected' : 'Not setup'}`}>
                  <span className={`${platform}-icon-wrap`} style={{display: 'flex'}}>
                    {getPlatformIcon(platform)}
                  </span>
                  <span className="status-dot" style={{width: '6px', height: '6px', background: isConnected ? 'var(--status-success)' : 'var(--text-muted)', borderRadius: '50%'}}></span>
                </div>
              );
            })
          )}
        </div>
      </div>

      {postResult ? (
        /* Results View */
        <div className="results-card glass-panel" style={{padding: '24px'}}>
          <div className="results-header-status" style={{marginBottom: '20px'}}>
            <div className={`results-badge-main ${postResult.success ? 'success' : 'failure'}`} style={{width: '50px', height: '50px', fontSize: '1.5rem', margin: '0 auto 10px'}}>
              {postResult.success ? <CheckIcon /> : <CrossIcon />}
            </div>
            <h2 style={{fontSize: '1.2rem'}}>{postResult.success ? 'Post Published!' : 'Failed to Publish'}</h2>
          </div>

          <div className="results-list" style={{gap: '12px', marginBottom: '20px'}}>
            {postResult.results.map((r, idx) => (
              <div key={idx} className="result-row" style={{padding: '12px 16px', borderRadius: '8px'}}>
                <div className="result-platform-info" style={{gap: '8px'}}>
                  <span className={`result-status-icon ${r.success ? 'success' : 'error'}`}>
                    {r.success ? <CheckIcon /> : <CrossIcon />}
                  </span>
                  <span className={`${r.platform.toLowerCase()}-icon-wrap`}>
                    {getPlatformIcon(r.platform.toLowerCase())}
                  </span>
                  <span style={{fontSize: '0.9rem', fontWeight: '600'}}>{r.platform}</span>
                </div>
                <div>
                  {r.success ? (
                    r.url ? (
                      <a href={r.url} target="_blank" rel="noopener noreferrer" className="result-link" style={{padding: '4px 8px', fontSize: '0.8rem'}}>
                        Link <ExternalLinkIcon />
                      </a>
                    ) : (
                      <span style={{color: 'var(--text-secondary)', fontSize: '0.8rem'}}>OK</span>
                    )
                  ) : (
                    <span style={{color: 'var(--status-error)', fontSize: '0.8rem', fontStyle: 'italic'}} title={r.error}>Error</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <button type="button" className="reset-btn" onClick={resetForm} style={{padding: '12px'}}>
            Create New Post
          </button>
        </div>
      ) : (
        /* Minimal Creator Form */
        <form className="creator-card glass-panel" onSubmit={handleSubmit} style={{padding: '24px', gap: '20px'}}>
          {/* Caption */}
          <div className="form-group" style={{gap: '6px'}}>
            <label className="form-label" style={{fontSize: '0.85rem'}}>Post Caption</label>
            <textarea
              className="form-textarea"
              placeholder="Write update text..."
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              style={{minHeight: '100px', fontSize: '0.9rem'}}
              required
            />
          </div>

          {/* Drag & Drop File Zone */}
          <div className="form-group" style={{gap: '6px'}}>
            <label className="form-label" style={{fontSize: '0.85rem'}}>Attach Image File</label>
            {imageFile ? (
              <div className="image-preview-container" style={{padding: '10px'}}>
                <img src={imagePreviewUrl} alt="Upload preview" className="preview-thumbnail" style={{width: '50px', height: '50px'}} />
                <div className="preview-meta">
                  <div className="preview-filename" style={{fontSize: '0.8rem'}}>{imageFile.name}</div>
                  <div className="preview-filesize" style={{fontSize: '0.7rem'}}>{(imageFile.size / (1024 * 1024)).toFixed(2)} MB</div>
                </div>
                <button type="button" className="remove-image-btn" onClick={removeSelectedFile} style={{width: '24px', height: '24px'}}>
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
                style={{padding: '24px 16px', gap: '8px'}}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  className="file-input-hidden"
                  accept="image/jpeg,image/png,image/gif"
                  onChange={handleFileChange}
                />
                <span className="upload-icon" style={{color: 'var(--text-secondary)'}}><UploadIcon /></span>
                <span className="upload-prompt" style={{fontSize: '0.85rem'}}>Drag image here, or click to upload</span>
              </div>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="submit-btn"
            disabled={isPosting || !caption.trim()}
            style={{padding: '14px', fontSize: '0.95rem', marginTop: '10px'}}
          >
            {isPosting ? (
              <>
                <span className="spinner" style={{width: '16px', height: '16px'}}></span>
                Publishing to all active channels...
              </>
            ) : (
              <>Publish Post</>
            )}
          </button>
        </form>
      )}

      {/* Toasts */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`} style={{padding: '10px 14px', fontSize: '0.85rem'}}>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
