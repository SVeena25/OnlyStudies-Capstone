# How to Add Images to Blog Posts

## Prerequisites: Set Up Cloudinary

Since Heroku uses ephemeral storage, you need to use Cloudinary for persistent image storage.

### 1. Get Cloudinary Credentials

1. Visit [cloudinary.com](https://cloudinary.com) and create a free account
2. Go to your Dashboard after logging in
3. Find your credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

### 2. Configure Cloudinary on Heroku

Run this command in your terminal (replace with your actual credentials):

```powershell
heroku config:set CLOUDINARY_URL="cloudinary://YOUR_API_KEY:YOUR_API_SECRET@YOUR_CLOUD_NAME" -a only-studies
```

Example format:
```powershell
heroku config:set CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME" -a only-studies
```

### 3. Remove the Image Clearing Command

Since we want to keep images now, remove the command from Procfile:

Edit the `Procfile` and change:
```
release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py clear_featured_images
```

To:
```
release: python manage.py migrate && python manage.py collectstatic --noinput
```

Then deploy:
```powershell
git add Procfile
git commit -m "Remove clear_featured_images from release phase"
git push heroku main
```

## Adding Images to Blog Posts

### Method 1: Through Django Admin Panel

1. Log in to the admin panel: `https://only-studies-61de8e7773bd.herokuapp.com/admin/`
2. Navigate to **App_onlystudies** → **Blog posts**
3. Click on the blog post you want to edit
4. Scroll to the **Featured image** field
5. Click "Choose File" and select your image
6. Click **Save**

The image will be automatically uploaded to Cloudinary and displayed on your site.

### Method 2: Through the Edit Blog Post Form

1. Log in to your site
2. Go to the blog post you authored
3. Click the **Edit** button
4. Under "Current Featured Image", click "Choose File" to upload a new image
5. Click **Update Blog Post**

### Method 3: When Creating a New Post

1. Log in and go to your blog feed or admin panel
2. Create a new blog post
3. Fill in the required fields (Title, Content, Category)
4. Upload an image in the "Featured image" field
5. Click **Save** or **Create**

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## Image Best Practices

- **Recommended dimensions**: 1200x675 pixels (16:9 aspect ratio)
- **Maximum file size**: Keep under 2MB for faster loading
- **Optimize images**: Use tools like TinyPNG before uploading
- **Use descriptive filenames**: e.g., "python-tutorial-beginners.jpg"

## Troubleshooting

### Images not appearing after upload?

1. Check that CLOUDINARY_URL is set correctly:
   ```powershell
   heroku config:get CLOUDINARY_URL -a only-studies
   ```

2. Verify it doesn't contain placeholder text like `<your_api_key>`

3. Check the Heroku logs for errors:
   ```powershell
   heroku logs --tail -a only-studies
   ```

### Images showing 404 errors?

- This means Cloudinary isn't configured. Follow Step 2 above.
- Make sure you've deployed after setting the config variable.

### Want to test locally?

1. Add your CLOUDINARY_URL to `env.py`:
   ```python
   os.environ['CLOUDINARY_URL'] = 'cloudinary://YOUR_API_KEY:YOUR_API_SECRET@YOUR_CLOUD_NAME'
   ```

2. Make sure `env.py` is in `.gitignore` (it already is)
3. Run your local server and upload images

## Current Status

- ✅ Blog post model supports featured images
- ✅ Templates display images with responsive sizing
- ✅ Placeholder icons shown when no image exists
- ✅ Lazy loading enabled for performance
- ⚠️ **Action Required**: Set up Cloudinary credentials (see Step 2)
