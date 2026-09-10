import { generatePlan } from "@/lib/circadian/engine";
import type { PlanInput } from "@/lib/circadian/types";

export async function POST(request: Request) {
  try {
    const input = (await request.json()) as PlanInput;
    const plan = generatePlan(input);
    return Response.json(plan);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Could not generate plan";
    return Response.json({ error: message }, { status: 400 });
  }
}
