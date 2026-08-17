from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.maddex.Card import Card, CardContent, CardDescription, CardHeader, CardTitle
from src.lib.maddex.Field import Field, FieldDescription, FieldGroup, FieldLabel
from src.lib.maddex.Input import Input


@component
def SigninPanel():
    return html(r"""
<main class="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
  <x-card class="w-full max-w-sm">
    <x-card-header>
      <x-card-title>Login to your account</x-card-title>
      <x-card-description>
        Enter your email below to login to your account.
        <p class="mt-2 text-red-500" hidden="{!requestError}">{requestError}</p>
      </x-card-description>
    </x-card-header>
    <x-card-content>
      <form onsubmit="handleSignin(event)">
        <x-field-group>
          <x-field>
            <x-field-label for="email">Email</x-field-label>
            <x-input name="email"
                     id="email"
                     type="email"
                     placeholder="m@example.com"
                     autocomplete="email"
                     required />
          </x-field>
          <x-field>
            <div class="flex items-center">
              <x-field-label for="password">Password</x-field-label>
              <a href="#"
                 class="ml-auto inline-block text-sm underline-offset-4 hover:underline">
                Forgot your password?
              </a>
            </div>
            <x-input name="password"
                     id="password"
                     type="password"
                     autocomplete="current-password"
                     required />
          </x-field>
          <x-field>
            <x-button type="submit" disabled="{loading}">
              {loading ? "Loading..." : "Login"}
            </x-button>
            <a href="/api/auth/signin/google"
               class="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 text-sm font-medium shadow-xs hover:bg-accent hover:text-accent-foreground">
              Login with Google
            </a>
            <x-field-description class="text-center">
              Don't have an account? <a href="#">Sign up</a>
            </x-field-description>
          </x-field>
        </x-field-group>
      </form>
    </x-card-content>

    <script>
      const [requestError, setRequestError] = pp.state("");
      const [loading, setLoading] = pp.state(false);

      async function handleSignin(event) {
        event.preventDefault();
        if (loading) return;

        setLoading(true);
        try {
          const data = Object.fromEntries(new FormData(event.currentTarget).entries());
          const response = await pp.rpc("signin", data, {
            url: window.location.pathname + window.location.search,
          });

          if (!response.success) {
            setRequestError(response.message);
            return;
          }

          setRequestError("");
        } finally {
          setLoading(false);
        }
      }
    </script>
  </x-card>
</main>
""")
