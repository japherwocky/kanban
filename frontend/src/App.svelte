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
  import NotFound from './routes/NotFound.svelte';

  onMount(() => {
    theme.init();
  });
</script>

<Router>
  <Route path="/login">
    <Login />
  </Route>

  <Route path="/boards">
    <BoardsList />
  </Route>

  <Route path="/boards/:id" let:params>
    <Board {params} />
  </Route>

  <Route path="/organizations">
    <Organizations />
  </Route>

  <Route path="/organizations/:id" let:params>
    <Organization {params} />
  </Route>

  <Route path="/admin" let:params>
    <Admin {params} />
  </Route>

  <Route path="/admin/:section" let:params>
    <Admin {params} />
  </Route>

  <Route path="/">
    <Landing />
  </Route>

  <Route path="*">
    <NotFound />
  </Route>
</Router>
