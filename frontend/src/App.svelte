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
  import Header from './lib/Header.svelte';
  import Footer from './lib/Footer.svelte';
  import Pricing from './routes/Pricing.svelte';
  import About from './routes/About.svelte';
  import Contact from './routes/Contact.svelte';
  import Privacy from './routes/Privacy.svelte';
  import Terms from './routes/Terms.svelte';

  onMount(() => {
    theme.init();
  });
</script>

<Router>
  <!-- Public pages with Header and Footer -->
  <div class="public-layout">
    <Header />
    <main>
      <Route path="/">
        <Landing />
      </Route>

      <Route path="/docs">
        <Docs />
      </Route>

      <Route path="/docs/:section" let:params>
        <Docs {params} />
      </Route>

      <Route path="/login">
        <Login />
      </Route>

      <Route path="/pricing">
        <Pricing />
      </Route>

      <Route path="/about">
        <About />
      </Route>

      <Route path="/contact">
        <Contact />
      </Route>

      <Route path="/privacy">
        <Privacy />
      </Route>

      <Route path="/terms">
        <Terms />
      </Route>
    </main>
    <Footer />
  </div>

  <!-- App pages (full-width, no Header/Footer) -->
  <div class="app-layout">
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
  </div>

  <Route path="*">
    <NotFound />
  </Route>
</Router>

<style>
  .public-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .public-layout main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .app-layout {
    min-height: 100vh;
  }
</style>
