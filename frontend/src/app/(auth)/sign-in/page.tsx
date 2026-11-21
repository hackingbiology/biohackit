// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SignInForm from "@/components/SignInForm";

export default function SignInPage() {
  const router = useRouter();
  const [lang, setLang] = useState<string>("en");
  useEffect(() => setLang(navigator.language), []);
  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <SignInForm lang={lang} onSignedIn={() => router.push("/dashboard")} />
    </main>
  );
}
