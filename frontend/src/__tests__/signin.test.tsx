// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SignInForm from "@/components/SignInForm";
import { orderProviders } from "@/lib/allauth";
import { pickLocale } from "@/lib/i18n";

function mockFetch(
  handlers: Record<string, { status: number; body: unknown }>,
) {
  global.fetch = jest.fn(async (url: string) => {
    const key = Object.keys(handlers).find((k) => String(url).endsWith(k))!;
    const h = handlers[key];
    return { status: h.status, json: async () => h.body } as Response;
  }) as unknown as typeof fetch;
}

const cfg = (providers: unknown[]) => ({
  "/config": { status: 200, body: { data: { socialaccount: { providers } } } },
});

// scenario: accounts-and-profiles::only-configured-providers-are-shown
test("only configured providers are shown, rapamycin.news first", async () => {
  mockFetch(
    cfg([
      { id: "google", name: "Google" },
      { id: "discourse_connect", name: "DiscourseConnect" },
    ]),
  );
  render(<SignInForm onSignedIn={() => {}} />);
  const items = await screen.findAllByRole("listitem");
  expect(items[0]).toHaveTextContent("rapamycin.news");
  expect(items[1]).toHaveTextContent("Google");
});

// scenario: accounts-and-profiles::only-configured-providers-are-shown
test("zero providers still offers email code", async () => {
  mockFetch(cfg([]));
  render(<SignInForm onSignedIn={() => {}} />);
  await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  expect(
    screen.getByRole("button", { name: "Email me a code" }),
  ).toBeInTheDocument();
});

// scenario: accounts-and-profiles::passwordless-sign-in
test("email code flow signs in", async () => {
  mockFetch({
    ...cfg([]),
    "/auth/code/request": { status: 401, body: {} },
    "/auth/code/confirm": {
      status: 200,
      body: { meta: { is_authenticated: true } },
    },
  });
  const done = jest.fn();
  render(<SignInForm onSignedIn={done} />);
  await userEvent.type(screen.getByLabelText("Email"), "a@b.co");
  await userEvent.click(
    screen.getByRole("button", { name: "Email me a code" }),
  );
  await userEvent.type(await screen.findByLabelText("Code"), "ABC123");
  await userEvent.click(screen.getByRole("button", { name: "Confirm" }));
  await waitFor(() => expect(done).toHaveBeenCalled());
});

test("bad code shows an alert", async () => {
  mockFetch({
    ...cfg([]),
    "/auth/code/request": { status: 401, body: {} },
    "/auth/code/confirm": { status: 400, body: {} },
  });
  render(<SignInForm onSignedIn={() => {}} />);
  await userEvent.type(screen.getByLabelText("Email"), "a@b.co");
  await userEvent.click(
    screen.getByRole("button", { name: "Email me a code" }),
  );
  await userEvent.type(await screen.findByLabelText("Code"), "x");
  await userEvent.click(screen.getByRole("button", { name: "Confirm" }));
  expect(await screen.findByRole("alert")).toBeInTheDocument();
});

test("locale is picked and ordering is stable", () => {
  expect(pickLocale("it-IT")).toBe("it");
  expect(pickLocale("zh-CN")).toBe("zh");
  expect(pickLocale("fr")).toBe("en");
  expect(orderProviders([{ id: "a", name: "A" }])).toHaveLength(1);
});
