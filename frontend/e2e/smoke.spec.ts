import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("landing sahifasi render bo'ladi va CTA bor", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "DarsPro" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Bepul boshlash/i })).toBeVisible();
});

test("landing → ro'yxatdan o'tish → kirish navigatsiyasi", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: /Bepul boshlash/i }).click();
  await expect(page).toHaveURL(/\/register$/);
  await expect(page.getByLabel("Email")).toBeVisible();
  await page.getByRole("link", { name: "Kirish" }).click();
  await expect(page).toHaveURL(/\/login$/);
});

test("o'quvchi kod-kirish sahifasi", async ({ page }) => {
  await page.goto("/play");
  await expect(page.getByPlaceholder("DRS-XXXX")).toBeVisible();
});

test("a11y: landing jiddiy buzilishlarsiz", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();
  const serious = results.violations.filter(
    (v) => v.impact === "serious" || v.impact === "critical"
  );
  expect(serious).toEqual([]);
});
