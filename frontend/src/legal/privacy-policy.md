# Realiti Privacy Policy

Last updated: October 12, 2026

Realiti is a platform where people share their experiences with real estate professionals. This policy explains what we collect, why, who receives it, and what you can do about it.

Realiti is operated by Anis Golriz, based in North Carolina. You can reach us at support@realiti.dev. This policy covers realiti.dev and everything we run under it. Realiti is in a testing period, so features and this policy may change.

## 1. Information we collect

**What you give us**

- Account: first name, last name, email and password. Your password is stored only as a one-way argon2 hash, so we cannot read it.
- Posts: a description, plus an optional title, experience rating, a tag, and an image or PDF.
- Activity: replies, likes and dislikes, and reports you file (a reason and an optional link to evidence).
- Professional verification: if you ask to be verified as a real estate professional, the name and state you work under, and any documents you submit to support your request.
- Support: anything you email to support@realiti.dev.

**Information about real estate professionals.** Users can add a real estate professional to our directory by name and the state they work in, even if that professional does not have a Realiti account.

**Uploaded files.** Images and PDFs can contain personal details, such as names, addresses or contract terms. Do not upload government IDs, financial account numbers, or anything you would not want our administrator and our moderation providers to see. We keep the original file name, so avoid personal details in file names.

**What we collect automatically.** Our servers log your IP address, the time, the page or endpoint requested, the response status, the referring page, and your browser's user agent. Cloudflare, which sits in front of our site, also sees each request.

**What we do not ask for.** We do not ask for your age, phone number, home address, payment details or government ID.

## 2. How we use information

- Run the service: create your account, sign you in, keep you signed in, and show your posts and replies.
- Moderate posts. Every new post is checked automatically, in this order:
  1. A text filter checks the title and description. Posts it flags are rejected.
  2. AWS Rekognition checks uploaded JPEG and PNG images. If it flags an image, the post is rejected and the image is deleted.
  3. Anthropic's Claude model reviews the title, description and any uploaded image or PDF. It can allow the post, reject it, or hold it for review by our administrator.
- Posts by verified real estate professionals go through the same checks, but the Claude review uses instructions written for posts by professionals.
- Automated checks make mistakes. If the Claude check cannot run or does not respond, the post may be published without that check. Replies are not checked automatically.
- Verify documents: our administrator can view a document attached to a post to decide whether to mark the post as verified, and can view documents a professional submits to decide whether to mark them as verified.
- Protect the service: detect abuse, enforce rate limits, and keep the site secure. We check new passwords against a list of known breached passwords.
- Respond to you: answer support emails and reports.
- Meet legal obligations and enforce our Terms of Service.

We do not sell your personal information, and we do not use it for advertising.

## 3. Who receives your information

We use the service providers below. Each receives only what its job requires. All of our infrastructure is in the United States.

| Provider | What it does for us | What it receives |
| --- | --- | --- |
| Amazon Web Services | Hosts the app and database, stores uploaded files, scans images | All account and content data, and uploaded files |
| Anthropic (Claude API) | Reviews posts for policy violations | Post title and description, and uploaded images or PDFs. Not your name, email or user ID. |
| Cloudflare | DNS, security, analytics, email forwarding | Every request to the site, including IP address and browser details, and support emails it forwards |
| Have I Been Pwned | Checks passwords against known breaches | The first 5 characters of a hash of your password, never the password itself |
| Google (Gmail) | Receives support email that Cloudflare forwards | Support emails you send us |

Anthropic handles content sent through its commercial API under its own terms. Under those terms, API content is not used to train its models, and Anthropic deletes it within 30 days, except where it must keep content longer to enforce its usage policy or comply with the law.

We may also disclose information if the law requires it, to protect people's safety or our rights, or if Realiti is transferred to a new owner.

## 4. What is public and what is private

**Public, with no login required**

- Published posts: your first name, your numeric user ID, the title, description, experience rating, a post tag, like and dislike counts, and verification status. The verification status shows whether a post has a document waiting for review, so it reveals that a document was attached, though not the document itself.
- Replies: your first name, your numeric user ID, the reply text and the time you posted.
- Your post history: anyone can list all of your published posts by your user ID.
- The professional directory: each professional's name, the state they work in, and whether they are verified.

**Private**

- Your email address, which only you can see in your account.
- Your last name, which we collect but do not display.
- Your password hash.
- Uploaded images and PDFs, including documents submitted for professional verification. They are not shown to the public. Only our administrator and the providers listed above can access them.
- Who liked or disliked a post, and who filed a report.

**Keep in mind.** Public posts can be seen, copied and saved by anyone, including search engines and other sites. Deleting your account cannot recall those copies. Replies to a post that has been held or removed may remain viewable.

## 5. Cookies, logs and analytics

**Cookies and browser storage**

- Sign-in cookies: a refresh cookie and a matching security (CSRF) cookie keep you signed in for up to 30 days. They are used only for signing in. Your short-lived access token is held in your browser's memory, not in storage.
- Cloudflare security cookies: Cloudflare may set cookies to detect bots and bad traffic.
- Display preference: your browser may remember a light or dark theme choice.
- We do not use advertising cookies, tracking pixels, fingerprinting, or third-party analytics trackers.

**Analytics.** We use Cloudflare Web Analytics. It works from request data Cloudflare already sees, sets no cookies, and adds no script to our pages.

**Server logs.** Our logs record IP address, time, requested page, response status, referring page and browser user agent. They do not record your user ID, email or tokens. Moderation activity, including the storage key of uploaded files and image-scan labels, is also written to server logs. We do not apply a fixed retention period; logs are cleared when we rebuild the server.

**Rate limiting.** To block abuse we limit login and signup attempts by IP address. These counters are kept in memory only and reset when the server restarts.

## 6. How long we keep information, and deletion

- Account and posts: kept while your account exists.
- Deleting your account: you can delete your account from the Account page by entering your password. This permanently deletes your account, your posts, your replies, your likes and dislikes, the reports you filed, and all replies, likes, dislikes and reports on your posts.
- Uploaded files: deleting your account does not automatically delete files you uploaded. They stay in private storage until we delete them. Email support@realiti.dev and we will.
- Files from rejected posts: an image that AWS Rekognition flags is deleted right away. Files attached to posts rejected by the text filter or the Claude check are not deleted automatically. They stay in private storage until we delete them.
- Professional directory entries: an entry describes a professional, not an account, so deleting your account does not delete it. It only removes the link between the entry and your account. A professional who wants their entry corrected or removed can email support@realiti.dev.
- Removed and held posts: a post removed by our administrator or after an upheld report is hidden from the public but kept in our database. A post held for review is kept until it is reviewed.
- Individual posts and replies: you cannot edit or delete a single post or reply yourself. Email support@realiti.dev and we will review your request.
- Backups: database backups are kept for 1 day, so deleted data may remain in backups for up to about 2 days.
- Logs: see section 5.
- Support emails: kept as long as we need them to help you and keep records.

## 7. Your choices and rights

You can ask us to access, correct, or delete the personal information we hold about you, including a change to your name or email, which the app does not let you edit. Email support@realiti.dev from the address on your account. We will acknowledge your request within 3 business days and complete it within 30 days. Depending on where you live, privacy law may give you additional rights, and we will honor reasonable requests wherever you are.

You can delete your account at any time (see section 6). There is no automatic data export; email us and we will send you a copy of your account data.

## 8. Security

Traffic to Realiti is encrypted over HTTPS, our database and file storage are encrypted at rest, our file storage is private, passwords are hashed with argon2 and checked against known breaches, and sign-in tokens are short-lived. No system is perfectly secure, so we cannot guarantee absolute security. Use a strong, unique password.

## 9. Children

Realiti is for people 18 and older. We do not knowingly collect information from anyone under 18. If we learn that we have, we will delete it.

## 10. Changes and contact

We may update this policy. We will post the new version with a new date, and if a change is significant we will tell users on the site. Questions or requests: support@realiti.dev.
