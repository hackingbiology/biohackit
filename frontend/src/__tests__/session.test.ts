// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import { logout } from "@/lib/auth";

test("logout ends the allauth session with DELETE", async () => {
  global.fetch = jest.fn(async () => ({
    status: 401,
    json: async () => ({}),
  })) as unknown as typeof fetch;
  await logout();
  const [url, init] = (global.fetch as jest.Mock).mock.calls[0] as [
    string,
    RequestInit,
  ];
  expect(url).toMatch(/\/_allauth\/browser\/v1\/auth\/session$/);
  expect(init.method).toBe("DELETE");
});
