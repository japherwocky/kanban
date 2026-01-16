<script>
  import { onMount } from 'svelte';
  import { Router, Route, Link } from 'svelte-routing';
  import { theme } from './lib/theme.js';

import Landing from './routes/Landing.svelte';
import Login from './routes/Login.svelte';
import BoardsList from './routes/BoardsList.svelte';
import Board from './routes/Board.svelte';
import Organizations from './routes/Organizations.svelte';
import Organization from './routes/Organization.svelte';
import Admin from './routes/Admin.svelte';
import Docs from './routes/Docs.svelte';
import NotFound from './routes/NotFound.svelte';
import ProtectedRoute from './lib/ProtectedRoute.svelte';

  onMount(() => {
    theme.init();
  });
</script>

<Router>
  <Route path="/login">
    <Login />
  </Route>

  <Route path="/boards">
    <ProtectedRoute>
      <BoardsList />
    </ProtectedRoute>
  </Route>

  <Route path="/boards/:id" let:params>
    <ProtectedRoute>
      <Board {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/organizations">
    <ProtectedRoute>
      <Organizations />
    </ProtectedRoute>
  </Route>

  <Route path="/organizations/:id" let:params>
    <ProtectedRoute>
      <Organization {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/admin" let:params>
    <ProtectedRoute>
      <Admin {params} />
    </ProtectedRoute>
  </Route>

<Route path="/admin/:section" let:params>
    <ProtectedRoute>
      <Admin {params} />
    </ProtectedRoute>
  </Route>

  <Route path="/docs">
    <Docs />
  </Route>

  <Route path="/docs/:section" let:params>
    <Docs {params} />
  </Route>

  <Route path="/">
    <Landing />
  </Route>

  <Route path="*">
    <NotFound />
  </Route>
</Router>
