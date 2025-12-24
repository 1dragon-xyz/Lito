# Vercel Deployment Fix and Optimization

## Status: Completed

## Objective
Fix the "Not Found" error on `https://lito-web.vercel.app/` by restructuring the project for optimal Vercel deployment (static files + serverless API).

## Steps

- [x] **Analyze Directory Structure**
    - [x] Identified `web-app` as the root for web deployment.
    - [x] Identified mixed static (`index.html`) and API (`api/index.py`) content.

- [x] **Restructure for Vercel**
    - [x] Create `web-app/public` directory (standard for static assets).
    - [x] Move `index.html`, `app.js`, `style.css` to `web-app/public`.
    - [x] Keep `api/` and `requirements.txt` in project root (`web-app/`).

- [x] **Configuration Update**
    - [x] Update `vercel.json` to explicitly use `builds` and `rewrites`.
    - [x] Map `/api/(.*)` to Python backend.
    - [x] Map `/(.*)` to `public/` directory for static serving.

- [x] **Deployment**
    - [x] Run `vercel --prod`.
    - [x] Confirmed successful deployment to `https://1dragon.xyz` (aliased).

## Verification
- User should check `https://lito-web.vercel.app/` or `https://1dragon.xyz`.
