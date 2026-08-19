# Regenerating package-lock.json

`npm ci` is used by CI (`.github/workflows/ci.yml`) and by production
(`sys/scripts/deploy.sh`), so the committed lockfile has to work on Linux,
Windows and macOS alike.

## The trap

npm records only the optional dependencies it actually resolved for the host
platform ([npm/cli#4828](https://github.com/npm/cli/issues/4828)). Several of
this project's build dependencies ship their native code that way:

| package | native binary |
| --- | --- |
| `rollup` (via vite) | `@rollup/rollup-<platform>` |
| `tailwindcss` | `@tailwindcss/oxide-<platform>` |
| `lightningcss` | `lightningcss-<platform>` |
| `esbuild` (via vite) | `@esbuild/<platform>` |

A lockfile pruned to one platform makes `npm ci` fail everywhere else, with no
native binary installed at all:

    Error: Cannot find module @rollup/rollup-linux-x64-gnu

That is not a lockfile you can fix in place. npm treats an existing
`package-lock.json` **and an existing `node_modules`** as the starting tree and
will not re-expand optional dependencies that were pruned out of it, so
`npm install --package-lock-only` on top of a pruned lockfile just reproduces
it. Both have to be gone first.

## The recipe

From `frontend/`, on any OS:

    rm -rf node_modules package-lock.json
    npm install --package-lock-only
    npm ci

Deleting **both** is the whole trick. With no tree to prune against, npm keeps
every platform's optional dependencies, and the result is portable. Then
`npm ci` puts your own `node_modules` back.

## Verifying

The lockfile should name binaries for platforms you are not on:

    grep -c '"node_modules/@rollup/rollup-' package-lock.json

Expect ~25, spanning `linux`, `win32` and `darwin`. If it returns 2, it was
regenerated against an existing tree — start over with both removed.

`npm ci` then installs only the entries matching the current platform and skips
the rest as os/cpu mismatches, which is exactly the intent.
