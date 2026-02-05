# Runbook - Monitoring and Incident Response

Operations guide for monitoring, alerting, and responding to incidents in the Gong Call Coaching frontend application.

## Table of Contents

- [Overview](#overview)
- [Monitoring](#monitoring)
- [Alerting](#alerting)
- [Incident Response](#incident-response)
- [Common Incidents](#common-incidents)
- [Escalation](#escalation)
- [Post-Incident](#post-incident)

## Overview

### Roles and Responsibilities

**On-Call Engineer**:
- Monitor alerts and dashboards
- Respond to incidents within SLA
- Perform initial triage and troubleshooting
- Escalate when needed
- Document incidents

**Engineering Lead**:
- Escalation point for critical incidents
- Coordinate complex incident response
- Make architectural decisions during incidents
- Review post-incident reports

**DevOps Team**:
- Infrastructure and deployment support
- Vercel and backend services
- Database and external service issues

### Service Level Objectives (SLOs)

**Availability**: 99.9% uptime (43 minutes downtime per month)

**Performance**:
- Page load time (P95): < 2 seconds
- API response time (P95): < 500ms
- Time to First Byte (TTFB): < 200ms

**Response Times**:
- SEV-1 (Critical): 15 minutes
- SEV-2 (High): 1 hour
- SEV-3 (Medium): 4 hours
- SEV-4 (Low): Next business day

## Monitoring

### Key Metrics to Monitor

#### Application Health

**Availability**:
- Vercel deployment status
- API route availability
- Authentication service (Clerk) availability
- MCP backend availability

**Error Rates**:
- 4xx errors (client errors)
- 5xx errors (server errors)
- Authentication failures
- API timeout rate

**Performance**:
- Core Web Vitals (LCP, FID, CLS)
- API route P95 latency
- Page load times
- Time to Interactive (TTI)

#### Traffic Metrics

**Usage**:
- Active users (daily/weekly/monthly)
- Page views per user
- API calls per user
- Feature adoption rates

**Geographic Distribution**:
- User locations
- Regional performance differences
- CDN hit rates

### Monitoring Tools

#### Vercel Analytics

**Access**: [Vercel Dashboard](https://vercel.com) → Project → Analytics

**Key Views**:
- Real-time traffic
- Page views and unique visitors
- Top pages by traffic
- Geographic distribution
- Referrers and user agents

**Usage**:
```bash
# View analytics via CLI
vercel logs --follow
```

#### Vercel Speed Insights

**Access**: Vercel Dashboard → Project → Speed Insights

**Metrics**:
- Largest Contentful Paint (LCP): < 2.5s
- First Input Delay (FID): < 100ms
- Cumulative Layout Shift (CLS): < 0.1

**Alerts**:
- Set up alerts for Core Web Vitals degradation
- Notify when metrics exceed thresholds

#### Function Logs

**Access**: Vercel Dashboard → Deployments → Select deployment → Functions

**What to Monitor**:
- Error logs in API routes
- Function execution duration
- Cold start frequency
- Memory usage

**CLI Access**:
```bash
# Tail production logs
vercel logs --follow

# Filter by function
vercel logs --follow --path=/api/coaching/analyze-call

# View specific deployment
vercel logs <deployment-url>
```

#### Custom Logging

**Client-Side Error Tracking**:

```typescript
// app/layout.tsx - Add error boundary
'use client';

import { useEffect } from 'react';

export function ErrorBoundary({ error }: { error: Error }) {
  useEffect(() => {
    // Log to monitoring service
    console.error('Client error:', error);

    // Could integrate Sentry, DataDog, etc.
    // reportError(error);
  }, [error]);

  return <div>Something went wrong. Please refresh.</div>;
}
```

**Server-Side Logging**:

API routes automatically log errors via `lib/api-logger.ts`:
- Request/response logs
- Error logs with stack traces
- Performance metrics

#### External Service Monitoring

**Clerk Status**:
- [Clerk Status Page](https://status.clerk.com)
- Subscribe to updates

**MCP Backend Health**:
```bash
# Check backend health endpoint
curl https://coaching-api.prefect.io/health

# Expected response
{"status": "healthy"}
```

**Vercel Status**:
- [Vercel Status Page](https://www.vercel-status.com)
- Subscribe to updates

### Dashboard Setup

**Recommended Dashboard Layout**:

1. **Overview Panel**:
   - Current deployment status
   - Active users (last 5 minutes)
   - Error rate (last hour)
   - P95 response time

2. **Traffic Panel**:
   - Requests per minute (last 24h)
   - Unique users (last 24h)
   - Top pages

3. **Errors Panel**:
   - Recent errors (last 1h)
   - Error rate trend
   - Top error messages

4. **Performance Panel**:
   - Core Web Vitals
   - API route latencies
   - Slow pages (> 2s load time)

## Alerting

### Alert Channels

**Slack** (recommended):
- Channel: `#engineering-alerts`
- Critical alerts: @channel mention
- Normal alerts: No mention

**Email**:
- Critical alerts: engineering@prefect.io
- Normal alerts: on-call@prefect.io

**PagerDuty** (optional):
- Critical incidents only
- Routes to on-call engineer

### Alert Configuration

#### Vercel Deployment Alerts

**Setup**:
1. Vercel Dashboard → Settings → Notifications
2. Add integration (Slack or email)
3. Select events:
   - Deployment failed
   - Deployment ready (production only)

**Alert Rules**:
- **Deployment Failed** → SEV-2
- **Deployment Succeeded After Failure** → Info

#### Error Rate Alerts

**Setup** (requires custom monitoring):

```javascript
// Pseudo-code for error rate alerting
if (errorRate > 5% over 5 minutes) {
  alert('SEV-2: High error rate');
}

if (errorRate > 10% over 5 minutes) {
  alert('SEV-1: Critical error rate');
}
```

**Alert Rules**:
- **> 5% errors** → SEV-2 (High)
- **> 10% errors** → SEV-1 (Critical)
- **> 50% errors** → SEV-1 (Critical) + Page

#### Performance Alerts

**Core Web Vitals Degradation**:
- LCP > 4s for 10 minutes → SEV-3
- FID > 300ms for 10 minutes → SEV-3
- CLS > 0.25 for 10 minutes → SEV-3

**API Latency**:
- P95 > 1s for 5 minutes → SEV-3
- P95 > 2s for 5 minutes → SEV-2

#### Availability Alerts

**Frontend Down**:
- Cannot reach production URL → SEV-1
- Health check failing → SEV-1

**Backend Down**:
- MCP backend health check failing → SEV-1
- All API requests failing → SEV-1

**Authentication Down**:
- Clerk service unavailable → SEV-1
- Cannot sign in → SEV-1

### Alert Severity Levels

**SEV-1 (Critical)**:
- Complete service outage
- Data loss or corruption
- Security breach
- **Response**: 15 minutes
- **Escalation**: Immediate to Engineering Lead

**SEV-2 (High)**:
- Partial service degradation
- High error rate (> 5%)
- Performance significantly degraded
- **Response**: 1 hour
- **Escalation**: After 1 hour if not resolved

**SEV-3 (Medium)**:
- Minor degradation
- Isolated feature issues
- Non-critical bugs
- **Response**: 4 hours
- **Escalation**: Next business day if not resolved

**SEV-4 (Low)**:
- Minor bugs
- Enhancement requests
- Documentation issues
- **Response**: Next business day
- **Escalation**: Not required

## Incident Response

### Incident Response Process

#### 1. Detection and Acknowledgment

**When Alert Fires**:
1. Acknowledge alert immediately
2. Check monitoring dashboard
3. Verify incident is real (not false positive)
4. Create incident ticket/channel

**Commands**:
```bash
# Check current deployment status
vercel ls

# Check recent deployments
vercel ls --limit 10

# View logs
vercel logs --follow
```

#### 2. Triage and Assessment

**Determine Severity**:
- How many users affected?
- Is service completely down or degraded?
- Is data at risk?
- Are critical workflows blocked?

**Gather Information**:
- What changed recently? (deployments, config)
- When did issue start?
- What's the error rate?
- Which components are affected?

**Communication**:
```
# Slack message template (SEV-1/SEV-2)
@channel 🚨 INCIDENT - SEV-<level>

**Issue**: <brief description>
**Impact**: <who/what is affected>
**Status**: Investigating
**Owner**: @<your-name>

Updates will be posted in thread.
```

#### 3. Mitigation and Resolution

**Immediate Actions** (in order of preference):

1. **Rollback Deployment** (fastest):
   ```bash
   # List recent deployments
   vercel ls

   # Promote last known good deployment
   vercel promote <deployment-url>
   ```

2. **Disable Problematic Feature**:
   - Feature flag if available
   - Emergency code change + deploy

3. **Scale Resources** (if performance issue):
   - Not applicable to Vercel (auto-scales)
   - Check backend capacity

4. **Fix Root Cause**:
   - Fix bug
   - Test locally
   - Deploy fix
   - Verify resolution

**Verification**:
- Check monitoring for improvement
- Test affected functionality
- Confirm error rate decreased
- Verify user reports

#### 4. Communication

**During Incident**:
- Post updates every 15 minutes (SEV-1) or 30 minutes (SEV-2)
- Update status in Slack thread
- Notify stakeholders of ETR (Estimated Time to Resolution)

**Example Update**:
```
🔍 Update 12:15 PM

**Status**: Mitigating
**Action**: Rolled back to deployment abc123
**Impact**: Error rate decreased from 20% to 2%
**Next**: Monitoring for 10 minutes, then will mark resolved
```

**Resolution Message**:
```
✅ RESOLVED

**Issue**: [description]
**Duration**: 32 minutes (12:00 PM - 12:32 PM)
**Impact**: ~150 users experienced errors
**Resolution**: Rolled back deployment with bug in API route
**Next Steps**: Root cause analysis, deploy fix tomorrow

Post-incident review scheduled for [date/time]
```

#### 5. Post-Incident Activities

See [Post-Incident](#post-incident) section below.

## Common Incidents

### Frontend Completely Down

**Symptoms**:
- Production URL not loading
- 503 Service Unavailable
- All users affected

**Likely Causes**:
- Deployment failure
- Vercel outage
- DNS issues
- Bad commit broke build

**Response**:

1. **Check Vercel Status**: [vercel-status.com](https://www.vercel-status.com)
   - If Vercel outage: Monitor and communicate, nothing to do

2. **Check Last Deployment**:
   ```bash
   vercel ls
   # Look for failed or error status
   ```

3. **Rollback Immediately**:
   ```bash
   # Promote previous working deployment
   vercel promote <previous-deployment-url>
   ```

4. **Verify Resolution**:
   - Visit production URL
   - Check error rate drops to zero

5. **Investigate Root Cause**:
   - Review failed deployment logs
   - Identify breaking change
   - Create fix PR

**Prevention**:
- Pre-deployment testing
- Gradual rollout (not available in Vercel free tier)
- Smoke tests after deployment

### High API Error Rate

**Symptoms**:
- 5xx errors in API routes
- Users seeing "Something went wrong"
- Timeouts

**Likely Causes**:
- MCP backend down or slow
- Database issues (if applicable)
- Bug in API route code
- Rate limiting backend

**Response**:

1. **Check Backend Health**:
   ```bash
   curl https://coaching-api.prefect.io/health
   ```

2. **Check API Logs**:
   ```bash
   vercel logs --follow --path=/api/coaching/*
   ```

3. **Identify Specific Endpoint**:
   - Which API route is failing?
   - Is it all routes or specific ones?

4. **If Backend Issue**:
   - Escalate to backend team
   - Consider showing degraded UI
   - Communicate impact to users

5. **If Frontend Bug**:
   - Rollback deployment
   - Fix bug
   - Deploy fix

**Prevention**:
- Health check endpoints
- Graceful degradation
- Better error handling
- Backend monitoring

### Authentication Failures

**Symptoms**:
- Users cannot sign in
- "Unauthorized" errors
- Session expired messages

**Likely Causes**:
- Clerk service outage
- Invalid Clerk API keys
- CORS issues
- Middleware configuration error

**Response**:

1. **Check Clerk Status**: [status.clerk.com](https://status.clerk.com)

2. **Verify Clerk Keys**:
   ```bash
   # Check environment variables are set (don't print values)
   vercel env ls
   ```

3. **Test Authentication**:
   - Try signing in with test account
   - Check browser console for errors
   - Check Network tab for failed Clerk requests

4. **If Clerk Outage**:
   - Monitor Clerk status page
   - Post communication to users
   - Nothing to fix on our end

5. **If Configuration Issue**:
   - Verify environment variables
   - Check middleware.ts
   - Rollback if recent change

**Prevention**:
- Monitor Clerk status
- Test auth in preview deployments
- Have backup authentication method (future)

### Slow Performance

**Symptoms**:
- Pages loading slowly
- High P95 latency
- Core Web Vitals degraded

**Likely Causes**:
- Large JavaScript bundle
- Unoptimized images
- Slow API requests
- Database query performance

**Response**:

1. **Check Speed Insights**:
   - Identify slow pages
   - Check which metrics degraded (LCP, FID, CLS)

2. **Check API Latency**:
   ```bash
   # Look for slow API routes
   vercel logs --follow
   ```

3. **Recent Changes**:
   - What was deployed recently?
   - New dependencies added?
   - New images or assets?

4. **Quick Fixes**:
   - Revert recent performance-impacting changes
   - Enable caching if disabled
   - Optimize heavy pages

5. **Long-term Fixes**:
   - Bundle analysis
   - Code splitting
   - Image optimization
   - Database query optimization

**Prevention**:
- Performance budgets
- Bundle size monitoring
- Core Web Vitals testing
- Load testing

## Escalation

### When to Escalate

Escalate to Engineering Lead if:
- Incident is SEV-1 and not resolved in 30 minutes
- Incident is SEV-2 and not resolved in 2 hours
- Root cause is unclear after initial investigation
- Multiple systems affected
- Requires architectural decision
- Need additional resources

### Escalation Process

1. **Gather Context**:
   - What's been tried?
   - Current status?
   - Impact assessment?
   - Logs and error messages?

2. **Contact Lead**:
   - Slack DM + @mention in incident channel
   - Include incident summary
   - Request specific help needed

3. **Handoff (if needed)**:
   - Brief new responder
   - Share relevant logs/dashboards
   - Transfer incident ownership
   - Continue monitoring

### External Escalation

**Vercel Support**:
- Email: support@vercel.com
- Include: Project name, deployment URL, error description
- For critical issues: Mention "Production Down"

**Clerk Support**:
- Dashboard → Help & Support
- Include: Application ID, error details, timestamps

**Backend Team**:
- Slack: #backend-team
- Include: API endpoints affected, error rates, logs

## Post-Incident

### Incident Review Meeting

**Schedule**: Within 48 hours of resolution

**Attendees**:
- Incident responder(s)
- Engineering Lead
- Product Manager (for user-impacting incidents)
- Relevant stakeholders

**Agenda**:
1. Timeline of events
2. Root cause analysis
3. What went well
4. What could be improved
5. Action items

### Post-Incident Report

**Template**:

```markdown
# Post-Incident Report: [Title]

**Date**: YYYY-MM-DD
**Severity**: SEV-X
**Duration**: X hours Y minutes
**Impact**: [description of user impact]

## Summary
[Brief summary of what happened]

## Timeline
- HH:MM - Issue detected
- HH:MM - Incident declared
- HH:MM - Mitigation started
- HH:MM - Issue resolved
- HH:MM - Incident closed

## Root Cause
[Detailed explanation of what caused the incident]

## Impact Assessment
- **Users Affected**: ~X users
- **Requests Failed**: X%
- **Revenue Impact**: $X (if applicable)
- **Data Loss**: None / [description]

## Resolution
[How the incident was resolved]

## What Went Well
- [Things that worked well during response]

## What Could Be Improved
- [Things to improve for future incidents]

## Action Items
- [ ] [Action 1] - Owner: @name - Due: YYYY-MM-DD
- [ ] [Action 2] - Owner: @name - Due: YYYY-MM-DD

## Follow-up
[Any follow-up needed, monitoring, etc.]
```

### Follow-up Actions

**Immediate** (within 1 week):
- Fix root cause
- Add monitoring/alerting to catch earlier
- Update runbook with learnings
- Implement preventive measures

**Long-term** (within 1 month):
- Architectural improvements
- Process improvements
- Training based on incident
- Update documentation

## On-Call Rotation

### Rotation Schedule

**Recommended**:
- 1 week rotations
- Handoff on Monday morning
- Backup engineer identified
- Calendar invite with duties

### Handoff Process

**Outgoing Engineer**:
- Document any ongoing issues
- Share access credentials
- Brief incoming engineer
- Transfer monitoring access

**Incoming Engineer**:
- Review current system status
- Test alert channels
- Review recent incidents
- Ask questions

### On-Call Duties

**Daily**:
- Monitor dashboards
- Review overnight logs
- Check alert queue
- Respond to incidents

**Weekly**:
- Review incident trends
- Update runbook
- Test monitoring/alerting
- Coordinate with team on improvements

## Tools and Access

### Required Access

- [ ] Vercel dashboard access
- [ ] GitHub repository access
- [ ] Clerk dashboard access (admin)
- [ ] Slack access (#engineering-alerts)
- [ ] MCP backend logs access
- [ ] DNS management (for domain issues)

### Useful Commands

```bash
# Vercel CLI
vercel ls                    # List deployments
vercel logs --follow         # Tail logs
vercel promote <url>         # Rollback
vercel inspect <url>         # Deployment details

# Git
git log --oneline -10        # Recent commits
git revert <sha>             # Revert commit
git reset --hard <sha>       # Reset to commit

# System
curl -I https://url          # Check HTTP status
dig coaching.prefect.io      # Check DNS
ping coaching.prefect.io     # Check connectivity
```

### Useful Links

- [Vercel Dashboard](https://vercel.com/dashboard)
- [Clerk Dashboard](https://dashboard.clerk.com)
- [Vercel Status](https://www.vercel-status.com)
- [Clerk Status](https://status.clerk.com)
- [GitHub Repository](https://github.com/prefect/call-coach)

## Appendix

### Runbook Maintenance

This runbook should be updated:
- After each incident (add learnings)
- When processes change
- When new monitoring is added
- Quarterly review

**Owner**: Engineering Lead
**Last Updated**: February 2026
**Next Review**: May 2026
