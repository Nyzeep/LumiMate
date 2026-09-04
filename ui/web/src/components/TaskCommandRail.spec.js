import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import TaskCommandRail from "./TaskCommandRail.vue";

describe("TaskCommandRail", () => {
  it("offers one plan-approval command beside an explicit reject danger zone", async () => {
    const wrapper = mount(TaskCommandRail, {
      props: { task: { state: "awaiting_plan_approval" }, stateLabel: "等待计划确认" }
    });

    const rail = wrapper.get('[aria-label="任务命令"]');
    const approve = rail.get('button[aria-label="确认计划"]');
    const reject = rail.get('button[aria-label="危险操作：拒绝计划"]');
    expect(rail.findAll("button")).toHaveLength(2);
    expect(wrapper.get('[aria-label="危险操作区"]')).toBeTruthy();

    await approve.trigger("click");
    await reject.trigger("click");
    expect(wrapper.emitted("plan-decision")).toEqual([[true], [false]]);
  });

  it("maps a permission request to paired allow and reject decisions", async () => {
    const wrapper = mount(TaskCommandRail, {
      props: { task: { state: "running", permission: { category: "filesystem" } }, stateLabel: "等待权限" }
    });

    await wrapper.get('button[aria-label="允许"]').trigger("click");
    await wrapper.get('button[aria-label="危险操作：拒绝权限"]').trigger("click");
    expect(wrapper.emitted("permission-decision")).toEqual([[true], [false]]);
  });

  it("maps a running task to pause and cancel without offering unrelated task commands", async () => {
    const wrapper = mount(TaskCommandRail, {
      props: { task: { state: "running" }, stateLabel: "运行中" }
    });

    const rail = wrapper.get('[aria-label="任务命令"]');
    expect(rail.get('button[aria-label="暂停任务"]')).toBeTruthy();
    expect(rail.get('button[aria-label="危险操作：取消任务"]')).toBeTruthy();
    expect(rail.find('button[aria-label="恢复任务"]').exists()).toBe(false);
    await rail.get('button[aria-label="危险操作：取消任务"]').trigger("click");
    expect(wrapper.emitted("cancel")).toHaveLength(1);
  });
});
