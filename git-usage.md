## Git Usage/Policies

1. For each "unit of work" you are doing, create a new branch.
Typically this means for a ticket or small bugfix. Name your branch in a descriptive manner.

`git checkout main` (always switch to `main` first unless you are sure you know what you're doing!)
`git switch -c color-theme-change`

2. Once you're on the branch, use git as you usually would, making commits as you make progress.

`git add main.css`

`git commit -m "updated CSS for blue theme"`

`git push -u origin color-theme-change`
(the -u portion may be required once, then you can use `git push`)

3. When you are ready for someone else to review your work create a PR here:

<https://github.com/uchicago-mscapp-projects/public-data-portal/pulls>

Describe what you've changed, and mention any areas you'd like people to pay special attention to.

4. Reviewers will review (see **Code Review** below) and leave feedback.

Respond to any requests for changes either by making the change or discussing on the ticket.

If you receive the go-ahead to merge, please **merge your own work** by pressing the green button on the PR page.

Once the work is merged, you may **delete the branch**, github will prompt you to do this.

Note: Unless you click past 1-2 big red buttons, it is very unlikely you'll lose work. Deleting an unmerged branch is intentionally difficult.

### Updating/Back to Main

Whenever it is time to start a new branch, start on `main`, the recommended flow is:

```shell
$ git switch main         # back to main
$ git pull origin main    # update to latest
$ git switch -c new-branch 
```

This is also true if you need to work on two things at once, but hopefully we can avoid that.

## Code Review

1. Read through the code once to get a general understanding of what it does.
  - If you see bugs or anything very surprising/confusing comment as you go, but for now focus on a quick understanding of the change.

2. Take a second pass through now that you understand the code,
  - What isn't clear?
  - Are there any "code smells" (duplicated code, unused code, non-idiomatic code, etc.)

Leave your comments, be constructive with your feedback, and remember the goal is that we all have a better understanding of the problem, not that the code is *exactly* as you'd like it.

For now, if there are significant issues that you think should be addressed, mark as **Changes Requested**, otherwise you can mark as OK to merge.
