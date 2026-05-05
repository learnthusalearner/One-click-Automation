# Autoposter

Simple one-click social media posting. Upload one image, write your caption once — it posts to LinkedIn, Instagram, and Facebook automatically.

---

## Project Structure

```
autoposter/
├── .env.example          ← copy to .env and fill in credentials
├── .env                  ← your secrets (never commit this)
├── requirements.txt
├── config.py             ← loads & validates all env vars
├── main.py               ← CLI entry point
├── platforms/
│   ├── __init__.py
│   ├── base.py           ← abstract base class (PostPayload, PostResult)
│   ├── facebook.py       ← Facebook Graph API adapter
│   ├── instagram.py      ← Instagram Graph API adapter
│   └── linkedin.py       ← LinkedIn UGC Posts API adapter
└── utils/
    ├── __init__.py
    └── image.py          ← image validation + conversion helpers
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Then open `.env` and fill in your API keys (see **Getting Credentials** below).

### 3. Verify config

```bash
python main.py check-config
```

---

## Usage

### Post to all platforms (one-click)

```bash
python main.py post \
  --image photo.jpg \
  --description "Just launched our new product — months of work finally live!"
```

Or with short options:

```bash
python main.py post -i photo.jpg -d "Your caption here"
```

That's it! Your image and caption will be posted to Facebook, Instagram, and LinkedIn automatically.

### Check your config

```bash
python main.py check-config
```

---

## Getting Credentials

### Facebook
1. Go to https://developers.facebook.com → My Apps → Create App
2. Add **Pages API** product
3. Use Graph API Explorer → select your Page → generate token with:
   - `pages_manage_posts`
   - `pages_read_engagement`
4. Set `FACEBOOK_PAGE_ID` (your Page's numeric ID) and `FACEBOOK_ACCESS_TOKEN`

### Instagram
Instagram publishes via the **Meta Graph API** linked to a Facebook Business Page.

1. Connect your Instagram Professional account to a Facebook Page
2. In Graph API Explorer, get your **Instagram Business Account ID**:
   ```
   GET /me/accounts → find your page → GET /{page-id}?fields=instagram_business_account
   ```
3. Generate a token with:
   - `instagram_basic`
   - `instagram_content_publish`
4. Set `INSTAGRAM_ACCOUNT_ID` and `INSTAGRAM_ACCESS_TOKEN`
5. **Important:** Instagram requires a **public image URL** — local file uploads are not supported. Either host your image (Imgur, Cloudinary, S3) and pass `--image-url`, or set `IMAGE_HOST_URL` in `.env`.

### LinkedIn
1. Go to https://developer.linkedin.com → My Apps → Create App
2. Add **Share on LinkedIn** and **Sign In with LinkedIn** products
3. Under Auth, generate an access token with scopes:
   - `w_member_social`
   - `r_liteprofile`
4. Get your Person URN:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.linkedin.com/v2/me
   # Look for "id" in the response — your URN is urn:li:person:{id}
   ```
5. Set `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_AUTHOR_URN`

---

## Adding a New Platform

1. Create `platforms/yourplatform.py`
2. Subclass `BasePlatform` and implement `name` and `publish()`
3. Add your config dataclass to `config.py`
4. Register the adapter in `main.py`'s `_build_platform_adapters()`

---

## Notes

- Access tokens expire. Facebook/Instagram tokens last ~60 days; use the Token Debugger to extend them.
- LinkedIn tokens expire after 60 days by default.
- Never commit your `.env` file. Add it to `.gitignore`.
