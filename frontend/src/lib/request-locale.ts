// SPDX-License-Identifier: AGPL-3.0-or-later
import { headers } from "next/headers";
import { pickLocale, type Locale } from "@/lib/i18n";

/** Locale from the first tag of the Accept-Language request header. */
export async function requestLocale(): Promise<Locale> {
  const header = (await headers()).get("accept-language") ?? undefined;
  return pickLocale(header?.split(",")[0]?.trim());
}
