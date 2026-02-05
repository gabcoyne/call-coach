# Deployment Checklist

Use this checklist when deploying the Call Coach frontend to Vercel. Reference the detailed [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) guide for step-by-step instructions.

## Pre-Deployment Checklist

### Code Readiness
- [ ] All tests passing (`npm run test`)
- [ ] No TypeScript errors (`npm run lint`)
- [ ] Successful local build (`cd frontend && npm run build`)
- [ ] Code reviewed and approved (GitHub PR)
- [ ] CHANGELOG.md updated with version and changes

### Environment Configuration
- [ ] `.env.example` up to date with all required variables
- [ ] Clerk production application created and configured
- [ ] Clerk production keys obtained (`pk_live_*` and `sk_live_*`)
- [ ] MCP backend production URL confirmed and accessible
- [ ] Custom domain DNS configured (`coaching.prefect.io`)

### Documentation
- [ ] README.md updated with deployment instructions
- [ ] API documentation current
- [ ] User guide reflects latest features

## Vercel Initial Setup (One-Time)

### Account and Project Setup
- [ ] Vercel account created with GitHub authentication
- [ ] GitHub repository linked to Vercel
- [ ] Project imported with Next.js framework preset
- [ ] Root directory set to `frontend/`
- [ ] Build and output directories verified

### Environment Variables (Production)
- [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` set
- [ ] `CLERK_SECRET_KEY` set
- [ ] `NEXT_PUBLIC_CLERK_SIGN_IN_URL` set to `/sign-in`
- [ ] `NEXT_PUBLIC_CLERK_SIGN_UP_URL` set to `/sign-up`
- [ ] `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` set to `/dashboard`
- [ ] `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` set to `/dashboard`
- [ ] `NEXT_PUBLIC_MCP_BACKEND_URL` set to production URL
- [ ] `NEXT_PUBLIC_APP_URL` set to `https://coaching.prefect.io`

### Environment Variables (Preview/Staging)
- [ ] All above variables configured for Preview environment
- [ ] Clerk test keys used for Preview (`pk_test_*` and `sk_test_*`)
- [ ] MCP backend staging URL configured

### Domain and SSL
- [ ] Custom domain `coaching.prefect.io` added to Vercel
- [ ] DNS CNAME record configured (points to `cname.vercel-dns.com`)
- [ ] DNS verification successful
- [ ] SSL certificate automatically provisioned and active
- [ ] Domain set as primary domain
- [ ] HTTPS redirects enabled

### Deployment Settings
- [ ] Production branch set to `main`
- [ ] Automatic production deployments enabled
- [ ] Preview deployments enabled for all branches
- [ ] GitHub branch protection rules configured

### Security Configuration
- [ ] `vercel.json` security headers verified
- [ ] CSP (Content Security Policy) configured
- [ ] HSTS (Strict-Transport-Security) enabled
- [ ] X-Frame-Options set to SAMEORIGIN
- [ ] Security headers scan passes (securityheaders.com)

### Monitoring and Notifications
- [ ] Slack integration added
- [ ] Deployment notifications channel configured
- [ ] Email notifications configured for production failures
- [ ] Vercel Analytics enabled
- [ ] Speed Insights enabled (optional)

## First Deployment Verification

### Deployment Process
- [ ] Initial deployment triggered (push to `main` or manual deploy)
- [ ] Build logs reviewed for warnings/errors
- [ ] Deployment completed successfully
- [ ] Deployment URL accessible

### Functionality Testing
- [ ] Homepage loads correctly
- [ ] Custom domain resolves (`https://coaching.prefect.io`)
- [ ] HTTPS certificate valid (no browser warnings)
- [ ] Sign-in page loads and redirects work
- [ ] Sign-up flow completes successfully
- [ ] Authentication persists across page reloads
- [ ] Dashboard loads with user data
- [ ] Call analysis page renders correctly
- [ ] Search functionality works
- [ ] API routes respond correctly
- [ ] Rep dashboard displays data
- [ ] Mobile responsive design verified

### Performance Testing
- [ ] Lighthouse audit score > 90 (Performance)
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] FID (First Input Delay) < 100ms
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] TTFB (Time to First Byte) < 600ms

### Security Testing
- [ ] Security headers present (check browser DevTools Network tab)
- [ ] CSP violations checked (no console errors)
- [ ] CORS configured correctly for MCP backend
- [ ] Authentication tokens stored securely (HttpOnly cookies)
- [ ] No sensitive data in client-side JavaScript
- [ ] XSS protection verified
- [ ] CSRF protection enabled (Clerk handles this)

## Preview Deployment Testing

### PR Preview Workflow
- [ ] Create test branch and open PR
- [ ] Vercel preview deployment triggered automatically
- [ ] Preview URL accessible from GitHub PR checks
- [ ] Preview uses staging environment variables
- [ ] Preview connects to staging MCP backend
- [ ] All functionality works in preview environment

### Preview Environment Validation
- [ ] Clerk test keys work correctly
- [ ] Staging backend data displayed
- [ ] No production data leaked to preview
- [ ] Preview URL format correct: `call-coach-git-<branch>-<team>.vercel.app`

## Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor deployment notifications in Slack
- [ ] Check error rates in Vercel Functions logs
- [ ] Review Core Web Vitals in Vercel Analytics
- [ ] Monitor user sign-ups and authentication success rate
- [ ] Check API route response times
- [ ] Review browser console errors (real user monitoring)

### First Week
- [ ] Weekly analytics review (traffic, performance, errors)
- [ ] User feedback collected and triaged
- [ ] Performance optimization opportunities identified
- [ ] Security scan repeated (securityheaders.com)
- [ ] Backup deployment tested (rollback procedure)

## Rollback Procedure (If Needed)

- [ ] Identify last known good deployment
- [ ] Navigate to Vercel Deployments tab
- [ ] Click three-dot menu on good deployment
- [ ] Select "Promote to Production"
- [ ] Verify rollback successful
- [ ] Notify team in Slack
- [ ] Create incident postmortem document

## Ongoing Maintenance

### Weekly Tasks
- [ ] Review Vercel Analytics dashboard
- [ ] Check for dependency updates (`npm outdated`)
- [ ] Review and respond to user feedback
- [ ] Monitor Core Web Vitals trends

### Monthly Tasks
- [ ] Security dependency updates (`npm audit`)
- [ ] Clerk dashboard review (user stats, authentication logs)
- [ ] Performance optimization review
- [ ] Cost analysis (Vercel usage, API calls)

### Quarterly Tasks
- [ ] Rotate Clerk API keys
- [ ] Review and update CSP rules
- [ ] Security audit (penetration testing)
- [ ] Disaster recovery drill (test rollback and restore)
- [ ] Documentation review and updates

## Emergency Contacts

- **Vercel Support**: Support tab in Vercel dashboard (Pro plan)
- **Clerk Support**: https://clerk.com/support
- **DNS/Domain Support**: [Your DNS provider support contact]
- **Team Lead**: [Name and contact]
- **On-Call Engineer**: [Pager/phone number]

## Additional Resources

- [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) - Detailed deployment guide
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Docs](https://nextjs.org/docs/deployment)
- [Clerk Next.js Guide](https://clerk.com/docs/quickstarts/nextjs)
- [Security Headers Best Practices](https://owasp.org/www-project-secure-headers/)

---

**Last Updated**: 2026-02-05
**Version**: 1.0.0
**Owner**: Engineering Team
