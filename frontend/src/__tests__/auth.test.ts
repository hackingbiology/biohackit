// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import { register, login } from "@/lib/auth";

function mockFetch(status: number, body: unknown) {
  global.fetch = jest.fn(async () => ({
    ok: status < 400,
    status,
    statusText: "",
    json: async () => body,
  })) as unknown as typeof fetch;
  return global.fetch as unknown as jest.Mock;
}

test("register() posts email/password to the register endpoint and returns tokens", async () => {
  const f = mockFetch(201, { access: "a", refresh: "r" });
  const out = await register("a@b.co", "pw-12345678");
  const [url, init] = f.mock.calls[0] as [string, RequestInit];
  expect(url).toMatch(/\/api\/auth\/register\/$/);
  expect(init.method).toBe("POST");
  expect(JSON.parse(init.body as string)).toEqual({
    email: "a@b.co",
    password: "pw-12345678",
  });
  expect(out).toEqual({ access: "a", refresh: "r" });
});

test("login() calls the token endpoint and returns access+refresh", async () => {
  const f = mockFetch(200, { access: "a", refresh: "r" });
  const out = await login("a@b.co", "pw-12345678");
  expect((f.mock.calls[0] as [string])[0]).toMatch(/\/api\/auth\/token\/$/);
  expect(out.access).toBe("a");
  expect(out.refresh).toBe("r");
});
