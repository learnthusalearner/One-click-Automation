# Steps to Fix Instagram Posting Issues

## 1. Diagnostic Findings

We ran a diagnostic check on your Meta Graph API setup and found the following:

* **Correction Done:** Your Facebook Page ID (`1155970660933898`) and Access Token were accidentally configured under the `INSTAGRAM` variables in `.env`. We have corrected this by moving them to `FACEBOOK_PAGE_ID` and `FACEBOOK_ACCESS_TOKEN`.
* **Current Status:** The Facebook Page *"Testingna"* currently has **no linked Instagram Business/Professional Account** (`instagram_business_account: None`), and the `INSTAGRAM` variables in `.env` are now left empty.

---

## 2. Steps to Resolve

To enable Instagram posting, you must connect a Professional Instagram account to your Facebook Page and configure the correct Instagram Business Account ID in your `.env` file.

### Step 2.1: Convert Instagram Account to Professional/Business (If not already)
1. Open the Instagram app on your phone.
2. Go to your **Profile** -> menu (three lines in top right) -> **Settings and activity**.
3. Scroll down and select **Account type and tools**.
4. Tap **Switch to professional account** (select **Business** or **Creator**).

### Step 2.2: Link Instagram to your Facebook Page
1. Go to your Facebook Page (*Testingna*) on a desktop browser.
2. Click **Manage** (or **Settings**).
3. Scroll down to **Linked Accounts** (under professional dashboard) or **Instagram**.
4. Click **Connect account** and log in with your Instagram Professional credentials to complete the link.

### Step 2.3: Retrieve the correct Instagram Business Account ID
Once linked, retrieve the ID by running this command in your terminal:
```powershell
python "C:\Users\KIIT\.gemini\antigravity-ide\brain\bb5029c9-56bd-4391-9190-9f67bfb5aaa2\scratch\debug_tokens.py"
```
Under **`--- Querying /me/accounts (Facebook Pages) ---`**, look for your Page name. You will now see:
`Linked Instagram Business Account: <New_Instagram_ID_Here>`

### Step 2.4: Update `.env` configuration
1. Open `backend/.env`.
2. Replace the `INSTAGRAM_ACCOUNT_ID` value with the new ID retrieved in Step 2.3.
3. Save the `.env` file.
4. Run the autoposter again:
   ```powershell
   $env:PYTHONIOENCODING="utf-8"
   python main.py post --image post/1.png --description "Post caption!"
   ```
