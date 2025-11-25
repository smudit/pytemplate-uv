# Projects Using Current Template

## Active Development Projects (High Priority)
*These projects have recent commits and active development*

1. **[Project Name Placeholder 1]**
   - Status: Active Development
   - Last Updated: [Date]
   - Migration Priority: High
   - Notes: Critical production service

2. **[Project Name Placeholder 2]**
   - Status: Active Development  
   - Last Updated: [Date]
   - Migration Priority: High
   - Notes: Customer-facing API

3. **[Project Name Placeholder 3]**
   - Status: Active Development
   - Last Updated: [Date]
   - Migration Priority: High
   - Notes: Data processing pipeline

## Maintenance Mode Projects (Medium Priority)
*These projects receive occasional updates and bug fixes*

4. **[Project Name Placeholder 4]**
   - Status: Maintenance
   - Last Updated: [Date]
   - Migration Priority: Medium
   - Notes: Internal tooling

5. **[Project Name Placeholder 5]**
   - Status: Maintenance
   - Last Updated: [Date]
   - Migration Priority: Medium
   - Notes: Reporting service

## Legacy Projects (Low Priority)
*These projects are stable with rare updates*

6. **[Project Name Placeholder 6]**
   - Status: Legacy
   - Last Updated: [Date]
   - Migration Priority: Low
   - Notes: Scheduled for deprecation

7. **[Project Name Placeholder 7]**
   - Status: Legacy
   - Last Updated: [Date]
   - Migration Priority: Low
   - Notes: Archive candidate

## Migration Strategy by Project Type

### Active Development (Weeks 5-8)
- Direct developer support
- Pair programming sessions
- Immediate issue resolution
- Rollback plan ready

### Maintenance Mode (Weeks 9-12)
- Self-service migration guide
- Slack support channel
- Weekly office hours
- Batch issue resolution

### Legacy Projects (Month 4+)
- Evaluate necessity
- Archive if unused
- Migrate only if required
- Minimal support

## Project Identification Script

To identify all projects using the template, run:

```bash
#!/bin/bash
# Script to find projects using our template

echo "Searching for projects with our template markers..."

# Search criteria (adjust based on your organization)
MARKERS=(
    "dynaconf"
    "loguru" 
    "typer"
    "from config import settings"
    "setup_logger"
)

# Search in organization repos (requires GitHub CLI)
for repo in $(gh repo list <your-org> --limit 1000 --json name -q '.[].name'); do
    echo "Checking $repo..."
    for marker in "${MARKERS[@]}"; do
        if gh api "repos/<your-org>/$repo/search/code?q=$marker" --jq '.items[0]' 2>/dev/null; then
            echo "✓ $repo uses our template"
            break
        fi
    done
done
```

## Data Collection Template

For each project identified:

```yaml
project_name: ""
repository_url: ""
status: "active|maintenance|legacy"
last_commit_date: ""
team_owner: ""
python_version: ""
dependencies_count: 0
has_ci_cd: false
deployment_target: "kubernetes|lambda|ec2|local"
migration_complexity: "low|medium|high"
migration_priority: "high|medium|low"
special_requirements: ""
contacts:
  - name: ""
    role: ""
    email: ""
```

## Next Steps

1. **Run Discovery Script**: Execute the project identification script
2. **Contact Team Leads**: Notify about upcoming migration
3. **Assess Complexity**: Review each project's customizations
4. **Create Timeline**: Schedule migration windows
5. **Identify Champions**: Find early adopters for pilot

## Metrics to Track

- Total projects identified: [TBD]
- Active development: [TBD]
- Maintenance mode: [TBD]
- Legacy/archived: [TBD]
- Average migration time estimate: [TBD]
- Resource requirements: [TBD]

## Notes

- This is a template document. Replace placeholder values with actual project information.
- Run the discovery script against your organization's repositories.
- Update the migration priorities based on business impact.
- Consider dependencies between projects when scheduling migrations.