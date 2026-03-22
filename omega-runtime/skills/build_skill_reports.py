#!/usr/bin/env python3

import html
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "omega-runtime/skills/OMEGA_SKILL_CATALOG.yaml"
DESCRIPTIONS_DIR = ROOT / "omega-runtime/skills/descriptions"
OUTPUT_HTML_DIR = ROOT / "output/html"
OUTPUT_REPORTS_DIR = ROOT / "output/reports"
MEMORY_REPORT_MD = ROOT / "output/reports/persistent-memory-status-report.md"
UI_SKILLS_BOUNDARY_GUIDE_MD = OUTPUT_REPORTS_DIR / "ui-skills-boundary-guide.md"
UI_SKILLS_BOUNDARY_CONTRACT_JSON = OUTPUT_REPORTS_DIR / "ui-skills-boundary-contract.json"
PMEM = Path.home() / ".codex/skills/persistent-memory/scripts/memory_cli.py"
SELF_LEARN = Path.home() / ".codex/skills/self-learn/scripts/run_self_learn.py"
OPENAI_DOC_LINKS = [
    {
        "label": "Code generation / Codex",
        "url": "https://developers.openai.com/api/docs/guides/code-generation/",
    },
    {
        "label": "Using GPT-5.4",
        "url": "https://developers.openai.com/api/docs/guides/latest-model/",
    },
    {
        "label": "GPT-5 new params and tools",
        "url": "https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_new_params_and_tools/",
    },
]
UI_GUIDE_OPENAI_DOC_LINKS = [
    {
        "label": "Apps SDK introduction",
        "url": "https://developers.openai.com/apps-sdk/quickstart/#introduction",
    },
    {
        "label": "Apps SDK web component",
        "url": "https://developers.openai.com/apps-sdk/quickstart/#build-a-web-component",
    },
    {
        "label": "Apps SDK decoupled pattern",
        "url": "https://developers.openai.com/apps-sdk/build/chatgpt-ui/#decoupled-pattern",
    },
]

REFRESHED_SKILLS = [
    "frontend-skill",
    "omega-ai-runtime",
    "omega-format",
    "omega-proof-gate",
    "omega-repo-map",
]
REMOVED_EXCEPTIONS = ["arabic-output-guard"]
SYSTEM_EXCEPTION_IDS = {"skill-creator", "skill-installer"}
MERGE_GROUPS = [
    {
        "tier": "S",
        "label_en": "Planning + Proof Stack",
        "label_ar": "باقة التخطيط والإثبات",
        "skills": ["god-plan-mode", "omega-repo-map", "plan-critic", "omega-proof-gate"],
        "why_en": "The four skills form one pipeline already: map the repo, shape the plan, critique the plan, then choose the proof package.",
        "why_ar": "الأربع مهارات دول شغالين فعليًا كسلسلة واحدة: نفهم الريبو، نبني الخطة، نراجعها، وبعدها نثبتها بأقل proof مقنع.",
        "action_en": "Best merge target: shared trigger contract or a coordinator wrapper before deeper consolidation.",
        "action_ar": "أفضل دمج مبدئي: عقد استدعاء موحد أو wrapper منسّق قبل أي دمج أعمق.",
    },
    {
        "tier": "A",
        "label_en": "Figma Source Chain",
        "label_ar": "سلسلة فيجما المصدرية",
        "skills": ["figma", "figma-implement-design", "figma_mcp_operator"],
        "why_en": "All three skills revolve around one design-source flow and differ mainly in control depth and workflow strictness.",
        "why_ar": "المهارات الثلاثة بتدور حول نفس مسار فيجما، والاختلاف الأساسي بينهم في درجة التحكم والصرامة التشغيلية.",
        "action_en": "Good candidate for a single entrypoint with modes: setup, implement, govern.",
        "action_ar": "مرشح قوي لمدخل واحد فيه modes: setup وimplement وgovern.",
    },
    {
        "tier": "A",
        "label_en": "UI Taste / System / Flow Cluster",
        "label_ar": "عنقود الذوق والنظام والتدفق",
        "skills": [
            "frontend-skill",
            "omega_ui_product_brain",
            "premium_ui_generator",
            "product_flow_architect",
            "design_system_enforcer",
            "ui_taste_critic",
        ],
        "why_en": "This cluster shares adjacent responsibilities across generation, critique, flow, and system enforcement, with one orchestration layer on top.",
        "why_ar": "العنقود ده فيه تداخل واضح بين التوليد والنقد والتدفق والـ design system، ومعاه skill orchestration فوقهم.",
        "action_en": "Keep the stack for now, but clarify handoff order and overlap boundaries in future revisions.",
        "action_ar": "الأفضل إبقاء الستاك الآن، لكن يحتاج ترتيب handoff أوضح وحدود overlap أهدى في النسخ القادمة.",
    },
    {
        "tier": "A",
        "label_en": "Structured Output Pipeline Chain",
        "label_ar": "سلسلة الـ Structured Output",
        "skills": [
            "portfolio-spectrum-builder",
            "schema-mapper",
            "jsonld-generator",
            "landing-generator",
            "seo-artifact-generator",
            "render-artifact-generator",
        ],
        "why_en": "These skills act as deterministic downstream stages. They are useful separately, but the chain is tightly coupled and easy to over-segment.",
        "why_ar": "المهارات دي شغالة كمراحل downstream حتمية. مفيدة وهي مفصولة، لكن الترابط عالي جدًا وسهل يتحول لتقسيم زائد.",
        "action_en": "Strong candidate for a grouped operator surface with stage-aware validation instead of many user-facing entrypoints.",
        "action_ar": "مرشح قوي لواجهة تشغيل مجمعة بوعي للمراحل بدل عدد كبير من entrypoints الظاهرة للمستخدم.",
    },
    {
        "tier": "B",
        "label_en": "OpenAI Runtime Pair",
        "label_ar": "ثنائي الـ OpenAI Runtime",
        "skills": ["openai-docs", "omega-ai-runtime"],
        "why_en": "One skill finds current source-of-truth docs, the other converts product ambiguity into runtime architecture; they are adjacent by design.",
        "why_ar": "واحدة تجيب source-of-truth الحالي، والتانية تحوله لعقد runtime عملي؛ الاتنين متجاورين طبيعيًا.",
        "action_en": "Do not fully merge yet, but keep them linked through explicit handoff notes.",
        "action_ar": "مش لازم يندمجوا كامل الآن، لكن لازم يبقى بينهم handoff أوضح ومعلن.",
    },
]
RETIRE_CANDIDATES = [
    {
        "skill": "yeet",
        "tier": "S",
        "reason_en": "Ultra-narrow explicit GitHub flow. High value when asked, low value as a default skill to carry mentally.",
        "reason_ar": "مهارة شديدة التخصص لمسار GitHub محدد جدًا. مفيدة عند الطلب الصريح، لكن حملها ذهنيًا بشكل دائم قيمته ضعيفة.",
        "instead_en": "Keep installed, but mentally classify it as an on-demand operator macro.",
        "instead_ar": "خليها موجودة، لكن اعتبرها macro تشغيلية عند الطلب فقط.",
    },
    {
        "skill": "vercel-deploy",
        "tier": "A",
        "reason_en": "Useful only at deployment time and already bounded by explicit user intent.",
        "reason_ar": "مفيدة وقت النشر فقط، ومقيدة أصلًا بطلب صريح من المستخدم.",
        "instead_en": "Keep as a specialist endpoint rather than a commonly considered path.",
        "instead_ar": "الأفضل اعتبارها endpoint متخصص وليس مسارًا نفكر فيه باستمرار.",
    },
    {
        "skill": "security-ownership-map",
        "tier": "A",
        "reason_en": "Powerful but extremely specific to security-history analysis and graph export workflows.",
        "reason_ar": "قوية، لكن متخصصة جدًا في تحليل الملكية الأمنية وتاريخ git وتصدير الجرافات.",
        "instead_en": "Treat as a specialist audit tool, not a default review skill.",
        "instead_ar": "تعامل معها كأداة audit متخصصة، لا كمهارة مراجعة افتراضية.",
    },
    {
        "skill": "doc",
        "tier": "B",
        "reason_en": "Narrow document-format workflow with clear activation. Valuable when needed, but easy to skip in general skill routing.",
        "reason_ar": "مسار وثائقي ضيق وواضح التفعيل. له قيمة عند الحاجة، لكنه سهل الاستبعاد من التفكير العام.",
        "instead_en": "Keep available as a task-specific file-format specialist.",
        "instead_ar": "يبقى متاحًا كمتخصص صيغة ملفات عند الحاجة فقط.",
    },
    {
        "skill": "spreadsheet",
        "tier": "B",
        "reason_en": "Same pattern as DOCX: strong in context, low value outside spreadsheet-heavy work.",
        "reason_ar": "نفس نمط DOCX تقريبًا: قوي داخل سياقه، وقيمته أقل خارج الأعمال المعتمدة على الجداول.",
        "instead_en": "Use only when the artifact itself is a spreadsheet.",
        "instead_ar": "استخدمها فقط لما يكون الـ artifact نفسه spreadsheet.",
    },
    {
        "skill": "speech",
        "tier": "B",
        "reason_en": "Audio generation is a real niche path, not a core routing primitive for most coding work.",
        "reason_ar": "توليد الصوت مسار niche حقيقي، وليس primitive أساسيًا في أغلب شغل الكود.",
        "instead_en": "Keep it as a media-specific capability behind explicit user demand.",
        "instead_ar": "الأفضل إبقاءها قدرة media متخصصة خلف طلب واضح من المستخدم.",
    },
]
IMPROVE_CANDIDATES = [
    {
        "skill": "omega-format",
        "tier": "S",
        "reason_en": "It sits on the user-facing surface and depends on a strict bypass matrix. Small mistakes here leak into every answer.",
        "reason_ar": "المهارة دي على السطح المباشر للمستخدم وتعتمد على bypass matrix حساس. أي خطأ بسيط فيها ينعكس على كل الردود.",
        "next_en": "Strengthen failure-mode examples and shared formatter verification.",
        "next_ar": "تحتاج أمثلة failure modes أوضح وتحققًا أقوى للـ shared formatter.",
    },
    {
        "skill": "openai-docs",
        "tier": "S",
        "reason_en": "The capability is strong, but it depends on MCP search quality and fast-moving official documentation.",
        "reason_ar": "القدرة نفسها قوية، لكن اعتمادها على جودة MCP search وعلى docs سريعة التغير يستحق tightening مستمر.",
        "next_en": "Improve canonical URL retrieval and document fallback reliability.",
        "next_ar": "الأولوية: تحسين جلب الـ canonical URLs وتثبيت fallback الرسمي بشكل أوضح.",
    },
    {
        "skill": "omega-ai-runtime",
        "tier": "S",
        "reason_en": "High-leverage design skill for AI features, but it lives on top of volatile model and surface guidance.",
        "reason_ar": "مهارة عالية الرافعة في تصميم أنظمة الذكاء، لكنها مبنية فوق guidance متغير في الموديلات والسطوح.",
        "next_en": "Keep the decision grid fresh and tighten explicit links to current OpenAI docs.",
        "next_ar": "تحتاج تحديثًا مستمرًا للـ decision grid وربطًا أوضح بالـ docs الحالية.",
    },
    {
        "skill": "self-learn",
        "tier": "A",
        "reason_en": "Its boundaries are healthy, but the current durable pattern count is still zero and the latest verification status remains rolled-back.",
        "reason_ar": "حدودها الحالية صحية، لكن عدد الـ durable patterns ما زال صفرًا وآخر verification status ما زال rolled-back.",
        "next_en": "Improve visible reporting and promotion criteria for genuinely reusable learnings.",
        "next_ar": "تحتاج reporting أوضح ومعايير ترقية أدق للتعلّمات القابلة لإعادة الاستخدام فعلًا.",
    },
    {
        "skill": "frontend-skill",
        "tier": "A",
        "reason_en": "The taste direction is strong, but it is still broad and can overlap with multiple adjacent UI skills.",
        "reason_ar": "الاتجاه الذوقي قوي، لكنه ما زال واسعًا ويتداخل مع عدة مهارات UI مجاورة.",
        "next_en": "Refine boundaries against orchestration, critique, and system-enforcement skills.",
        "next_ar": "المطلوب: حدود أدق أمام orchestration والنقد وdesign-system enforcement.",
    },
    {
        "skill": "sentry",
        "tier": "B",
        "reason_en": "The layered contract is thoughtful, but readiness states and later operations paths remain heavy for casual use.",
        "reason_ar": "العقد الطبقي مدروس، لكن readiness states ومسارات التشغيل اللاحقة ما زالت ثقيلة على الاستخدام العادي.",
        "next_en": "Simplify operator checkpoints and surface clearer phase transitions.",
        "next_ar": "يحتاج checkpoints أبسط وانتقالات أوضح بين المراحل.",
    },
]

UI_GOVERNANCE_OVERLAY = [
    {
        "skill_id": "god-plan-mode",
        "job": {
            "ar": "يقفل الهدف، يفصل facts عن assumptions، ويربط التنفيذ بالإثبات والمخاطر قبل ما نبدأ.",
            "en": "Locks the mission, separates facts from assumptions, and ties execution to proof and risk before work starts.",
        },
        "why": {
            "ar": "يُستدعى عندما تكون المهمة المركبة محتاجة contract واضح، لا كمهارة UI تنفيذية داخل العنقود نفسه.",
            "en": "Use it when a multi-step task needs a crisp execution contract, not as a peer UI skill inside the cluster.",
        },
    },
    {
        "skill_id": "plan-critic",
        "job": {
            "ar": "يضغط على الخطة قبل التنفيذ: dependency blind spots، verification theater، scope inflation، وضعف rollback.",
            "en": "Stress-tests the plan before execution for dependency blind spots, verification theater, scope inflation, and weak rollback.",
        },
        "why": {
            "ar": "يظهر كطبقة مراجعة للخطة، لا كمسار تصميم أو تحسين واجهة.",
            "en": "It belongs to plan review, not to interface design or refinement.",
        },
    },
    {
        "skill_id": "openai-docs",
        "job": {
            "ar": "يستدعى فقط عندما تكون الوثائق الرسمية الحالية قد تغيّر architecture أو surface contract أو validation.",
            "en": "Invoke it only when current official docs could change architecture, surface contracts, or validation.",
        },
        "why": {
            "ar": "في هذا العنقود دوره overlay توثيقي، وليس UI design skill.",
            "en": "Inside this cluster, it acts as a documentation overlay, not as a UI design skill.",
        },
    },
]

UI_COMPARISON_CONTRACT = [
    {
        "skill_id": "omega_ui_product_brain",
        "display_name": "Omega UI Product Brain",
        "layer": {"ar": "Orchestration", "en": "Orchestration"},
        "primary_job": {
            "ar": "يحدد mode التنفيذ، يحمي العناصر غير القابلة للكسر، ويرتّب المهارات الصحيحة بالترتيب الصحيح.",
            "en": "Selects the execution mode, protects non-negotiables, and routes the right skills in the right order.",
        },
        "first_choice_when": {
            "ar": "المهمة فيها أكثر من محور واحد: source + UX + taste + system أو فيها protected elements واضحة.",
            "en": "The task spans multiple axes: source + UX + taste + system, or it has explicit protected elements.",
        },
        "do_not_use_when": {
            "ar": "الطلب narrow وواضح ويحتاج pass واحد مباشر مثل visual critique فقط أو landing execution فقط.",
            "en": "The task is narrow and clear enough for a single direct pass like pure visual critique or direct landing execution.",
        },
        "inputs": [
            {
                "ar": "هدف المستخدم، القيود، الـsource truth إن وجد، وما الذي لا يجب تغييره.",
                "en": "User goal, constraints, source truth when present, and what must not change.",
            }
        ],
        "outputs": [
            {
                "ar": "active mode، protected elements، sequence، completion lock، وما الذي يُمنع downstream skills من كسره.",
                "en": "Active mode, protected elements, sequence, completion lock, and what downstream skills are not allowed to break.",
            }
        ],
        "protected_elements": [
            "user instruction",
            "task constraints",
            "source truth",
            "cta intent",
            "product-critical flow",
            "information architecture",
        ],
        "failure_modes": [
            {
                "ar": "استخدام لغة orchestration بدون اتخاذ sequence فعلي.",
                "en": "Using orchestration language without making an actual sequencing decision.",
            },
            {
                "ar": "تمرير كل مهمة على كل skills بلا داعٍ.",
                "en": "Sending every task through every skill without a reason.",
            },
            {
                "ar": "السماح لـtaste أو system أن يكسرا source أو flow بصمت.",
                "en": "Letting taste or system passes silently override source or flow.",
            },
        ],
        "handoff_to": [
            "figma_mcp_operator",
            "product_flow_architect",
            "ui_taste_critic",
            "design_system_enforcer",
            "premium_ui_generator",
        ],
        "overlap_with": ["frontend-skill"],
    },
    {
        "skill_id": "figma_mcp_operator",
        "display_name": "Figma MCP Operator",
        "layer": {"ar": "Source governance", "en": "Source governance"},
        "primary_job": {
            "ar": "يقرأ Figma، يستخرج structure قابل للتنفيذ، يوسم deviations، ويتحقق من parity.",
            "en": "Reads Figma, extracts implementation-relevant structure, labels deviations, and verifies parity.",
        },
        "first_choice_when": {
            "ar": "هناك Figma link أو frame أو node أو طلب parity source-based.",
            "en": "There is a Figma link, frame, node, or an explicit source-based parity request.",
        },
        "do_not_use_when": {
            "ar": "لا يوجد source design والمهمة generative بحتة.",
            "en": "There is no design source and the task is purely generative.",
        },
        "inputs": [
            {
                "ar": "رابط أو node من Figma، active mode، والسياق المطلوب الحفاظ عليه.",
                "en": "A Figma link or node, the active mode, and the context that must be preserved.",
            }
        ],
        "outputs": [
            {
                "ar": "extraction واضح لما هو preserved وما هو inferred وما هو changed.",
                "en": "A clear extraction of what is preserved, inferred, and changed.",
            }
        ],
        "protected_elements": ["source hierarchy", "component roles", "cta intent"],
        "failure_modes": [
            {
                "ar": "قراءة screenshot-only أو ادعاء parity بدون evidence.",
                "en": "Relying on screenshot-only reading or claiming parity without evidence.",
            },
            {
                "ar": "إعادة تصميم hierarchy بصمت في faithful work.",
                "en": "Silently redesigning hierarchy during faithful work.",
            },
        ],
        "handoff_to": ["premium_ui_generator", "ui_taste_critic", "design_system_enforcer"],
        "overlap_with": ["omega_ui_product_brain", "frontend-skill"],
    },
    {
        "skill_id": "product_flow_architect",
        "display_name": "Product Flow Architect",
        "layer": {"ar": "Product flow diagnosis", "en": "Product flow diagnosis"},
        "primary_job": {
            "ar": "يفحص goal clarity، الأولوية بين الأفعال، friction، trust، والحالات الناقصة.",
            "en": "Evaluates goal clarity, action priority, friction, trust, and missing states.",
        },
        "first_choice_when": {
            "ar": "المشكلة الأساسية ليست الشكل بل task path أو conversion أو next-step clarity.",
            "en": "The core problem is not appearance but the task path, conversion, or next-step clarity.",
        },
        "do_not_use_when": {
            "ar": "الطلب visual cleanup فقط أو token consistency فقط.",
            "en": "The request is only for visual cleanup or token consistency.",
        },
        "inputs": [
            {
                "ar": "الهدف المتوقع من المستخدم، CTA الحالية، والنقاط التي يضيع فيها المستخدم.",
                "en": "The user's likely goal, current CTAs, and the points where users get stuck.",
            }
        ],
        "outputs": [
            {
                "ar": "تشخيص task path + أولويات إصلاح flow + state coverage notes.",
                "en": "A task-path diagnosis plus flow priorities and state-coverage notes.",
            }
        ],
        "protected_elements": ["user goal", "primary action", "trust-sensitive steps", "critical states"],
        "failure_modes": [
            {
                "ar": "حل بصري جميل لكن task path ما زال مكسورًا.",
                "en": "A prettier surface that still leaves the task path broken.",
            },
            {
                "ar": "تقديم action قبل context أو ترك success/error states غامضة.",
                "en": "Showing action before context or leaving success/error states unclear.",
            },
        ],
        "handoff_to": ["premium_ui_generator", "ui_taste_critic", "design_system_enforcer"],
        "overlap_with": ["omega_ui_product_brain", "frontend-skill"],
    },
    {
        "skill_id": "ui_taste_critic",
        "display_name": "UI Taste Critic",
        "layer": {"ar": "Visual critique", "en": "Visual critique"},
        "primary_job": {
            "ar": "يرتّب مشاكل hierarchy وspacing وCTA emphasis وpolish حسب التأثير.",
            "en": "Prioritizes hierarchy, spacing, CTA emphasis, and polish issues by impact.",
        },
        "first_choice_when": {
            "ar": "الواجهة موجودة بالفعل والمطلوب sharper taste أو critique واضح لا إعادة هيكلة منتج كاملة.",
            "en": "The interface already exists and needs sharper taste or focused critique without a full product rethink.",
        },
        "do_not_use_when": {
            "ar": "المهمة source extraction أو system audit أو raw generation فقط.",
            "en": "The task is source extraction, a system audit, or raw generation only.",
        },
        "inputs": [
            {
                "ar": "واجهة قائمة أو mock قائم وملاحظة أن المشكلة في hierarchy أو polish.",
                "en": "An existing UI or mock where the issue is hierarchy or polish.",
            }
        ],
        "outputs": [
            {
                "ar": "verdict واضح + أعلى الإصلاحات تأثيرًا + premium polish pass.",
                "en": "A clear verdict, highest-impact fixes, and a premium polish pass.",
            }
        ],
        "protected_elements": ["working brand hierarchy", "existing product logic when not broken"],
        "failure_modes": [
            {
                "ar": "مجاملة غامضة أو critique بلا ترتيب أولويات.",
                "en": "Vague praise or critique with no priority order.",
            },
            {
                "ar": "تحويل critique إلى redesign صامت.",
                "en": "Letting critique silently turn into redesign.",
            },
        ],
        "handoff_to": ["premium_ui_generator", "design_system_enforcer"],
        "overlap_with": ["frontend-skill", "omega_ui_product_brain"],
    },
    {
        "skill_id": "design_system_enforcer",
        "display_name": "Design System Enforcer",
        "layer": {"ar": "System discipline", "en": "System discipline"},
        "primary_job": {
            "ar": "يعيد النظام إلى الواجهة: tokens، button roles، states، spacing scale، والـresponsive invariants.",
            "en": "Restores system behavior across tokens, button roles, states, spacing scale, and responsive invariants.",
        },
        "first_choice_when": {
            "ar": "هناك drift في الأزرار أو الحقول أو المسافات أو الحالات أو قواعد الـresponsive.",
            "en": "There is drift in buttons, fields, spacing, states, or responsive rules.",
        },
        "do_not_use_when": {
            "ar": "الطلب ideation بصري أو flow redesign أو source extraction.",
            "en": "The request is visual ideation, flow redesign, or source extraction.",
        },
        "inputs": [
            {
                "ar": "واجهة فيها قرارات متكررة لا تتصرف كقواعد.",
                "en": "A UI where repeated decisions no longer behave like rules.",
            }
        ],
        "outputs": [
            {
                "ar": "drift report + smallest corrections التي تعيد الانضباط بدون redesign.",
                "en": "A drift report plus the smallest corrections that restore order without redesign.",
            }
        ],
        "protected_elements": ["token roles", "component families", "emphasis rules", "responsive invariants"],
        "failure_modes": [
            {
                "ar": "اعتبار أي taste preference مشكلة نظام.",
                "en": "Treating any taste preference as a system problem.",
            },
            {
                "ar": "إعادة كتابة flow بدل إصلاح consistency.",
                "en": "Rewriting flow instead of fixing consistency.",
            },
        ],
        "handoff_to": ["premium_ui_generator"],
        "overlap_with": ["frontend-skill", "ui_taste_critic"],
    },
    {
        "skill_id": "premium_ui_generator",
        "display_name": "Premium UI Generator",
        "layer": {"ar": "Guided implementation", "en": "Guided implementation"},
        "primary_job": {
            "ar": "ينفذ pass واجهة أقوى تحت mode واضح وقيود معلنة بدل premium decoration العشوائي.",
            "en": "Executes a stronger UI pass under a clear mode and explicit constraints instead of random premium decoration.",
        },
        "first_choice_when": {
            "ar": "نحتاج تنفيذ refinement أو redesign controlled بعد وجود source/flow/taste/system inputs.",
            "en": "We need controlled refinement or redesign after source, flow, taste, or system inputs exist.",
        },
        "do_not_use_when": {
            "ar": "المطلوب review فقط أو source extraction فقط.",
            "en": "The task is review-only or source-extraction-only.",
        },
        "inputs": [
            {
                "ar": "active mode + critique findings + flow corrections + system rules أو source extraction.",
                "en": "Active mode plus critique findings, flow corrections, system rules, or source extraction.",
            }
        ],
        "outputs": [
            {
                "ar": "واجهة أقوى بصريًا ومنتجيًا مع disclosure واضح لما تغير.",
                "en": "A stronger UI outcome with clear disclosure of what changed.",
            }
        ],
        "protected_elements": ["active mode", "cta roles", "section order when protected", "component family rules"],
        "failure_modes": [
            {
                "ar": "premium شكلي بلا تحسن بنيوي.",
                "en": "Decorative premium styling with no structural improvement.",
            },
            {
                "ar": "تغيير flow أو source decisions بصمت.",
                "en": "Silently changing flow or source decisions.",
            },
        ],
        "handoff_to": ["ui_taste_critic", "design_system_enforcer"],
        "overlap_with": ["frontend-skill"],
    },
    {
        "skill_id": "frontend-skill",
        "display_name": "Frontend Skill",
        "layer": {"ar": "Single-pass visual doctrine", "en": "Single-pass visual doctrine"},
        "primary_job": {
            "ar": "يدفع التنفيذ إلى composition أقوى، hierarchy أوضح، motion intentional، وواجهة غير generic.",
            "en": "Pushes execution toward stronger composition, clearer hierarchy, intentional motion, and non-generic UI.",
        },
        "first_choice_when": {
            "ar": "الطلب net-new branded landing أو demo أو surface ذوقي تقوده art direction وليس source/flow/system complexity.",
            "en": "The request is a net-new branded landing, demo, or taste-led surface where art direction matters more than source/flow/system complexity.",
        },
        "do_not_use_when": {
            "ar": "المشكلة الأساسية Figma parity أو UX flow repair أو design-system drift أو protected elements معقدة.",
            "en": "The core problem is Figma parity, UX flow repair, design-system drift, or complex protected elements.",
        },
        "inputs": [
            {
                "ar": "brief بصري، brand presence مطلوب، ومساحة حرية مناسبة في composition.",
                "en": "A visual brief, a need for strong brand presence, and enough freedom in composition.",
            }
        ],
        "outputs": [
            {
                "ar": "واجهة poster-like أقوى مع visual thesis واضح، لكنها لا تنتج governance أو system audit أو flow diagnosis وحدها.",
                "en": "A stronger poster-like UI with a clear visual thesis, but not governance, system auditing, or flow diagnosis on its own.",
            }
        ],
        "protected_elements": ["visual anchor", "brand-first hierarchy", "sparse copy discipline", "no-cards-by-default bias"],
        "failure_modes": [
            {
                "ar": "استعمالها كبديل للمنظومة كلها، فتتسع فوق critique وsystem وorchestration.",
                "en": "Using it as a substitute for the whole stack, causing overlap with critique, system work, and orchestration.",
            },
            {
                "ar": "تقديم taste قوي مع product logic أو source safety أضعف من المطلوب.",
                "en": "Delivering strong taste while under-serving product logic or source safety.",
            },
        ],
        "handoff_to": ["ui_taste_critic", "design_system_enforcer"],
        "overlap_with": [
            "omega_ui_product_brain",
            "ui_taste_critic",
            "design_system_enforcer",
            "premium_ui_generator",
        ],
    },
]

UI_HUD_CONTRACT = {
    "cluster_summary": {
        "ar": "هذا العنقود ليس stack إلزامي يمر عليه كل طلب. هو خريطة routing: من يبدأ، من يراجع، ومتى تتوقف passes حتى لا يحدث drift.",
        "en": "This cluster is not a mandatory stack for every request. It is a routing map: who starts, who reviews, and where passes should stop to avoid drift.",
    },
    "handoff_order": [
        {
            "title": {"ar": "طبقة الحوكمة أولًا عند الحاجة", "en": "Governance first when needed"},
            "detail": {
                "ar": "استخدم `god-plan-mode` أو `plan-critic` أو `openai-docs` فقط إذا كانت الخطة أو الوثائق قد تغيّر القرار، وليس كمهارات UI peers.",
                "en": "Use `god-plan-mode`, `plan-critic`, or `openai-docs` only when planning or documentation can change the decision, not as peer UI skills.",
            },
            "skills": ["god-plan-mode", "plan-critic", "openai-docs"],
        },
        {
            "title": {"ar": "ابدأ بـ orchestration عندما تتعدد المحاور", "en": "Start with orchestration when axes multiply"},
            "detail": {
                "ar": "إذا كانت المهمة تجمع source أو flow أو taste أو system معًا، ابدأ بـ`omega_ui_product_brain`.",
                "en": "If the task mixes source, flow, taste, or system concerns, start with `omega_ui_product_brain`.",
            },
            "skills": ["omega_ui_product_brain"],
        },
        {
            "title": {"ar": "الـsource يسبق التوليد", "en": "Source before generation"},
            "detail": {
                "ar": "عند وجود Figma، يقرأ `figma_mcp_operator` المصدر قبل أي pass توليدي أو taste upgrade.",
                "en": "When Figma exists, `figma_mcp_operator` reads the source before any generative or taste-upgrade pass.",
            },
            "skills": ["figma_mcp_operator", "premium_ui_generator"],
        },
        {
            "title": {"ar": "الـflow يسبق polish إذا كان broken", "en": "Flow before polish when flow is broken"},
            "detail": {
                "ar": "إذا كانت المشكلة في CTA logic أو task path أو trust، يبدأ `product_flow_architect` قبل `ui_taste_critic`.",
                "en": "If the issue is CTA logic, task path, or trust, `product_flow_architect` should lead before `ui_taste_critic`.",
            },
            "skills": ["product_flow_architect", "ui_taste_critic"],
        },
        {
            "title": {"ar": "النظام يراجع الناتج قبل الإغلاق", "en": "System review closes the pass"},
            "detail": {
                "ar": "بعد التنفيذ أو refinement، يتأكد `design_system_enforcer` أن التحسينات لم تتحول إلى drift.",
                "en": "After implementation or refinement, `design_system_enforcer` checks that improvements did not become drift.",
            },
            "skills": ["design_system_enforcer"],
        },
        {
            "title": {"ar": "الاستثناء السريع: `frontend-skill`", "en": "Fast-path exception: `frontend-skill`"},
            "detail": {
                "ar": "يستطيع أن يقود وحده فقط عندما تكون المهمة taste-led وnet-new ولا تحمل source truth أو flow/system constraints ثقيلة.",
                "en": "It may lead alone only when the task is taste-led, net-new, and free of heavy source-truth or flow/system constraints.",
            },
            "skills": ["frontend-skill"],
        },
    ],
    "boundary_note": {
        "ar": "`frontend-skill` ليس orchestrator، وليس critique framework، وليس design-system enforcer. و`omega_ui_product_brain` ليس منفذ UI بحد ذاته.",
        "en": "`frontend-skill` is not an orchestrator, critique framework, or design-system enforcer. `omega_ui_product_brain` is not a UI executor by itself.",
    },
    "route_examples": [
        {
            "scenario_id": "figma_parity",
            "title": {"ar": "Figma parity", "en": "Figma parity"},
            "first_skill": "omega_ui_product_brain",
            "path": [
                "omega_ui_product_brain",
                "figma_mcp_operator",
                "premium_ui_generator",
                "ui_taste_critic",
                "design_system_enforcer",
            ],
            "note": {
                "ar": "هنا `frontend-skill` مرجع taste فقط إن لزم، لا قائد للمسار.",
                "en": "Here `frontend-skill` is only a taste reference if needed, not the route leader.",
            },
        },
        {
            "scenario_id": "visual_cleanup_only",
            "title": {"ar": "Visual cleanup only", "en": "Visual cleanup only"},
            "first_skill": "ui_taste_critic",
            "path": ["ui_taste_critic", "design_system_enforcer", "premium_ui_generator"],
            "note": {
                "ar": "لو اتسع النطاق أو ظهرت non-negotiables، ارفع المهمة إلى `omega_ui_product_brain`.",
                "en": "If the scope widens or non-negotiables appear, elevate the task to `omega_ui_product_brain`.",
            },
        },
        {
            "scenario_id": "ux_conversion_issue",
            "title": {"ar": "UX / conversion issue", "en": "UX / conversion issue"},
            "first_skill": "product_flow_architect",
            "path": ["product_flow_architect", "premium_ui_generator", "ui_taste_critic", "design_system_enforcer"],
            "note": {
                "ar": "لا تبدأ هنا بـ`frontend-skill` لأن المشكلة الأساسية ليست art direction بل completion logic.",
                "en": "Do not start with `frontend-skill` here because the issue is completion logic, not art direction.",
            },
        },
        {
            "scenario_id": "design_system_drift",
            "title": {"ar": "Design-system drift", "en": "Design-system drift"},
            "first_skill": "design_system_enforcer",
            "path": ["design_system_enforcer", "premium_ui_generator", "ui_taste_critic"],
            "note": {
                "ar": "النقطة هنا إعادة السلوك إلى قواعد، لا إعادة اختراع الواجهة.",
                "en": "The goal here is to restore rule-based behavior, not reinvent the interface.",
            },
        },
        {
            "scenario_id": "net_new_branded_landing",
            "title": {"ar": "Net-new branded landing", "en": "Net-new branded landing"},
            "first_skill": "frontend-skill",
            "path": ["frontend-skill", "ui_taste_critic", "design_system_enforcer"],
            "note": {
                "ar": "إذا دخل Figma أو IA ثابتة أو protected elements كثيرة، اجعل `omega_ui_product_brain` فوق المسار.",
                "en": "If Figma, fixed IA, or many protected elements appear, place `omega_ui_product_brain` above the route.",
            },
        },
        {
            "scenario_id": "dashboard_task_clarity",
            "title": {"ar": "Dashboard / task clarity weak", "en": "Dashboard / task clarity weak"},
            "first_skill": "product_flow_architect",
            "path": ["product_flow_architect", "premium_ui_generator", "design_system_enforcer"],
            "note": {
                "ar": "الهدف هنا ليس hero أجمل، بل أن يفهم operator ما الذي يفعله الآن وما الخطوة التالية.",
                "en": "The goal here is not a prettier hero, but making the operator understand what to do now and what comes next.",
            },
        },
    ],
    "authority_note": {
        "ar": "في التعارض: user instruction ثم constraints ثم source truth ثم product flow ثم design system ثم visual taste.",
        "en": "In conflicts: user instruction, then constraints, then source truth, then product flow, then design system, then visual taste.",
    },
}


def run_command(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True, cwd=ROOT)
    return result.stdout.strip()


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def extract_summary(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    summary_match = re.search(r"## Summary\n(.+?)(?:\n## |\Z)", text, re.S)
    if summary_match:
        return " ".join(line.strip() for line in summary_match.group(1).splitlines() if line.strip().startswith(("-",)) is False)
    heading_match = re.search(r"^# .+\n\n(.+?)(?:\n## |\Z)", text, re.M | re.S)
    if heading_match:
        first_block = " ".join(line.strip() for line in heading_match.group(1).splitlines() if line.strip())
        return first_block[:220]
    return "Summary unavailable."


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def bilingual_text(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    class_attr = f' class="{cls}"' if cls else ""
    return (
        f"<{tag}{class_attr}>"
        f'<span data-lang="ar">{escape(ar)}</span>'
        f'<span data-lang="en">{escape(en)}</span>'
        f"</{tag}>"
    )


def bilingual_html(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    class_attr = f' class="{cls}"' if cls else ""
    return (
        f"<{tag}{class_attr}>"
        f'<span data-lang="ar">{ar}</span>'
        f'<span data-lang="en">{en}</span>'
        f"</{tag}>"
    )


def code_chip(value: str) -> str:
    return f'<span class="chip chip-code">{escape(value)}</span>'


def pretty_timestamp(value: str) -> str:
    return value.replace("T", " ").replace("Z", " UTC")


def category_labels(category: str):
    labels = {
        "design": ("تصميم", "Design"),
        "io": ("ملفات وإخراج", "I/O"),
        "observability": ("رصد وتشغيل", "Observability"),
        "planning": ("تخطيط", "Planning"),
        "workspace": ("مسار عمل", "Workspace"),
        "openai": ("OpenAI", "OpenAI"),
        "security": ("أمن", "Security"),
        "automation": ("أتمتة", "Automation"),
        "system": ("نظام", "System"),
    }
    return labels.get(category, (category, category.title()))


COMPONENT_BASE = {
    "planning": {"execution": 33, "uniqueness": 15, "clarity": 12, "maintenance": 11, "evidence": 9},
    "openai": {"execution": 31, "uniqueness": 15, "clarity": 12, "maintenance": 10, "evidence": 9},
    "workspace": {"execution": 30, "uniqueness": 14, "clarity": 11, "maintenance": 10, "evidence": 8},
    "design": {"execution": 27, "uniqueness": 12, "clarity": 11, "maintenance": 10, "evidence": 7},
    "io": {"execution": 23, "uniqueness": 10, "clarity": 11, "maintenance": 12, "evidence": 6},
    "observability": {"execution": 24, "uniqueness": 11, "clarity": 10, "maintenance": 10, "evidence": 8},
    "automation": {"execution": 22, "uniqueness": 10, "clarity": 12, "maintenance": 12, "evidence": 5},
    "security": {"execution": 22, "uniqueness": 12, "clarity": 10, "maintenance": 9, "evidence": 8},
    "system": {"execution": 29, "uniqueness": 14, "clarity": 12, "maintenance": 11, "evidence": 8},
}

COMPONENT_OVERRIDES = {
    "god-plan-mode": {"execution": 5, "clarity": 2, "evidence": 2},
    "omega-repo-map": {"execution": 4, "uniqueness": 1, "clarity": 1},
    "plan-critic": {"execution": 3, "clarity": 2, "evidence": 1},
    "omega-proof-gate": {"execution": 3, "clarity": 1, "evidence": 2},
    "persistent-memory": {"execution": 4, "uniqueness": 3, "clarity": 1, "evidence": 2},
    "openai-docs": {"execution": 3, "uniqueness": 1, "clarity": 1, "evidence": 2},
    "omega-ai-runtime": {"execution": 3, "uniqueness": 2, "clarity": 1, "evidence": 1},
    "omega-format": {"execution": 2, "clarity": 2, "evidence": 1},
    "self-learn": {"execution": 2, "uniqueness": 2, "evidence": 2},
    "frontend-skill": {"execution": 3, "uniqueness": 1, "clarity": 1},
    "omega_ui_product_brain": {"execution": 2, "uniqueness": 2},
    "premium_ui_generator": {"execution": 2, "clarity": 1},
    "product_flow_architect": {"uniqueness": 2},
    "design_system_enforcer": {"clarity": 1, "evidence": 1},
    "ui_taste_critic": {"clarity": 1},
    "figma_mcp_operator": {"uniqueness": 2, "evidence": 1},
    "figma-implement-design": {"execution": 2},
    "figma": {"execution": 1},
    "portfolio-spectrum-builder": {"execution": 2, "clarity": 1},
    "schema-mapper": {"clarity": 1},
    "jsonld-generator": {"clarity": 1},
    "landing-generator": {"execution": 1},
    "seo-artifact-generator": {"execution": 1},
    "render-artifact-generator": {"execution": 1},
    "playwright": {"execution": 2, "uniqueness": 1},
    "pdf": {"execution": 1, "evidence": 1},
    "sentry": {"execution": 1, "uniqueness": 1},
    "security-threat-model": {"uniqueness": 1, "evidence": 1},
    "security-best-practices": {"evidence": 1},
    "teach_me": {"clarity": 2},
    "yeet": {"execution": -4, "maintenance": 1},
    "vercel-deploy": {"execution": -3, "maintenance": 1},
    "doc": {"execution": -1},
    "spreadsheet": {"execution": -1},
    "speech": {"execution": -1},
    "security-ownership-map": {"execution": -2},
}


def compute_components(skill_id: str, category: str):
    components = dict(COMPONENT_BASE[category])
    for key, value in COMPONENT_OVERRIDES.get(skill_id, {}).items():
        components[key] += value
    return components


def total_score(components) -> int:
    return sum(components.values())


def overall_tier(score: int) -> str:
    if score >= 86:
        return "S"
    if score >= 78:
        return "A"
    if score >= 69:
        return "B"
    return "C"


def tier_blurb(score: int) -> tuple[str, str]:
    if score >= 86:
        return ("رافعة تشغيلية عالية جدًا", "Very high operational leverage")
    if score >= 78:
        return ("قوي ويمكن الاعتماد عليه", "Strong and dependable")
    if score >= 69:
        return ("مفيد لكن ليس دائمًا أول اختيار", "Useful but not always first choice")
    return ("مسار تخصصي أو منخفض التكرار", "Specialist or low-frequency path")


def parse_memory_inspect(markdown_text: str):
    pairs = {}
    for line in markdown_text.splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            pairs[key.strip()] = value.strip()
    return {
        "language": pairs.get("Preferred language", "unknown"),
        "tone": pairs.get("Preferred tone", "unknown"),
        "role": pairs.get("Preferred assistant role", "unknown"),
        "plan": pairs.get("Planning style", "unknown"),
        "review": pairs.get("Review style", "unknown"),
        "project_id": pairs.get("Project id", "unknown"),
        "root_path": pairs.get("Root path", "unknown"),
        "aliases": pairs.get("Aliases", "unknown"),
        "domain": pairs.get("Domain", "unknown"),
        "memory_policy": pairs.get("Memory policy", "unknown"),
    }


def parse_triage(markdown_text: str):
    data = {}
    for line in markdown_text.splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            data[key.strip()] = value.strip()
    return {
        "project": data.get("Resolved project", "unknown"),
        "pending_total": int(data.get("Pending total", "0")),
        "promotable_total": int(data.get("Promotable total", "0")),
        "ephemeral_total": int(data.get("Ephemeral total", "0")),
        "conflict_count": int(data.get("Conflict count", "0")),
    }


def parse_suggest(output_text: str):
    entries = []
    pattern = re.compile(
        r"- `(?P<id>[^`]+)` \[project:[^\]]+\] (?P<key>[^ ]+) -> (?P<value>.+?) \| basis=(?P<basis>[^|]+) \| confidence=(?P<confidence>[^|]+) \| status=(?P<status>.+)$"
    )
    for line in output_text.splitlines():
        match = pattern.match(line.strip())
        if match:
            entries.append(match.groupdict())
    return entries


def parse_previous_memory_baseline():
    if not MEMORY_REPORT_MD.exists():
        return None
    text = MEMORY_REPORT_MD.read_text(encoding="utf-8")
    baseline = {}
    patterns = {
        "pending_total": r"Pending backlog: `(\d+)`",
        "promotable_total": r"Promotable: `(\d+)`",
        "ephemeral_total": r"Ephemeral: `(\d+)`",
        "conflict_count": r"Conflicts: `(\d+)`",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            baseline[key] = int(match.group(1))
    return baseline or None


def build_skill_index():
    catalog = read_yaml(CATALOG_PATH)
    skills = []
    for entry in catalog["entries"]:
        description_path = ROOT / entry["doc_path"]
        summary = extract_summary(description_path)
        is_exception = "/.system/" in entry["source_skill_path"]
        components = compute_components(entry["skill_id"], entry["category"])
        score = total_score(components)
        tier = overall_tier(score) if not is_exception else "EX"
        blurb_ar, blurb_en = tier_blurb(score)
        skill = {
            "skill_id": entry["skill_id"],
            "display_name": entry["display_name"],
            "category": entry["category"],
            "summary": summary,
            "source_path": entry["source_skill_path"],
            "doc_path": entry["doc_path"],
            "is_exception": is_exception,
            "components": components,
            "score": score,
            "tier": tier,
            "tier_blurb_ar": blurb_ar,
            "tier_blurb_en": blurb_en,
            "source_last_checked_at": entry["source_last_checked_at"],
            "doc_last_refreshed_at": entry["doc_last_refreshed_at"],
        }
        skills.append(skill)
    return skills


def build_memory_snapshot():
    inspect_text = run_command(["python3", str(PMEM), "inspect", "--cwd", str(ROOT), "--format", "markdown"])
    triage_text = run_command(["python3", str(PMEM), "triage", "--cwd", str(ROOT), "--format", "markdown"])
    suggest_text = run_command(["python3", str(PMEM), "suggest", "--cwd", str(ROOT)])
    doctor_text = run_command(["python3", str(PMEM), "doctor"])
    self_learn_json = json.loads(run_command(["python3", str(SELF_LEARN), "--intent", "report", "--json"]))
    inspect = parse_memory_inspect(inspect_text)
    triage = parse_triage(triage_text)
    suggest_entries = parse_suggest(suggest_text)
    key_counts = Counter(entry["key"] for entry in suggest_entries)
    baseline = parse_previous_memory_baseline()
    return {
        "inspect": inspect,
        "triage": triage,
        "suggest_entries": suggest_entries,
        "key_counts": key_counts,
        "doctor_text": doctor_text,
        "self_learn": self_learn_json,
        "baseline": baseline,
    }


def advice_flags(skill_id: str):
    flags = []
    if skill_id in REFRESHED_SKILLS:
        flags.append(("Refreshed", "محدَّث"))
    if any(skill_id in group["skills"] for group in MERGE_GROUPS):
        flags.append(("Merge Watch", "مراقبة دمج"))
    if any(skill_id == item["skill"] for item in RETIRE_CANDIDATES):
        flags.append(("Skip Watch", "مراقبة استبعاد"))
    if any(skill_id == item["skill"] for item in IMPROVE_CANDIDATES):
        flags.append(("Improve", "أولوية تحسين"))
    return flags


def render_skill_card(skill):
    category_ar, category_en = category_labels(skill["category"])
    advice = "".join(
        f'<span class="chip chip-muted"><span data-lang="ar">{escape(ar)}</span><span data-lang="en">{escape(en)}</span></span>'
        for en, ar in advice_flags(skill["skill_id"])
    )
    source_checked = pretty_timestamp(skill["source_last_checked_at"])
    doc_refreshed = pretty_timestamp(skill["doc_last_refreshed_at"])
    return f"""
      <article class="skill-card">
        <div class="skill-card__top">
          <div>
            <p class="eyebrow">skill_id</p>
            <h3>{escape(skill["display_name"])}</h3>
          </div>
          <div class="skill-card__score">
            <span class="tier-badge tier-{skill["tier"].lower()}">{escape(skill["tier"])}</span>
            <span class="score-badge">{skill["score"]}/100</span>
          </div>
        </div>
        <div class="chip-row">
          <span class="chip"><span data-lang="ar">{escape(category_ar)}</span><span data-lang="en">{escape(category_en)}</span></span>
          {advice}
        </div>
        {bilingual_text(skill["summary"], skill["summary"], "p", "skill-summary")}
        <div class="breakdown-grid">
          <div class="mini-stat"><span>E</span><strong>{skill["components"]["execution"]}/40</strong></div>
          <div class="mini-stat"><span>U</span><strong>{skill["components"]["uniqueness"]}/20</strong></div>
          <div class="mini-stat"><span>C</span><strong>{skill["components"]["clarity"]}/15</strong></div>
          <div class="mini-stat"><span>M</span><strong>{skill["components"]["maintenance"]}/15</strong></div>
          <div class="mini-stat"><span>G</span><strong>{skill["components"]["evidence"]}/10</strong></div>
        </div>
        {bilingual_text(skill["tier_blurb_ar"], skill["tier_blurb_en"], "p", "muted")}
        <div class="meta-list">
          <div><span>source_last_checked</span><strong>{escape(source_checked)}</strong></div>
          <div><span>doc_last_refreshed</span><strong>{escape(doc_refreshed)}</strong></div>
        </div>
      </article>
    """


def render_exception_card(skill):
    category_ar, category_en = category_labels(skill["category"])
    return f"""
      <article class="exception-card">
        <div class="chip-row">
          <span class="chip chip-warning">system exception</span>
          <span class="chip"><span data-lang="ar">{escape(category_ar)}</span><span data-lang="en">{escape(category_en)}</span></span>
        </div>
        <h3>{escape(skill["display_name"])}</h3>
        {bilingual_text(skill["summary"], skill["summary"], "p", "muted")}
        <p class="path-label">{escape(skill["source_path"])}</p>
      </article>
    """


def render_merge_group(group):
    skills_html = "".join(code_chip(skill) for skill in group["skills"])
    tier_class = group["tier"].lower()
    return f"""
      <article class="domain-card">
        <div class="domain-card__header">
          <span class="tier-badge tier-{tier_class}">{escape(group["tier"])}</span>
          {bilingual_text(group["label_ar"], group["label_en"], "h3")}
        </div>
        <div class="chip-row">{skills_html}</div>
        {bilingual_text(group["why_ar"], group["why_en"], "p", "domain-copy")}
        {bilingual_text(group["action_ar"], group["action_en"], "p", "muted")}
      </article>
    """


def render_candidate(candidate, kind: str):
    skill_id = candidate["skill"]
    return f"""
      <article class="domain-card">
        <div class="domain-card__header">
          <span class="tier-badge tier-{candidate["tier"].lower()}">{escape(candidate["tier"])}</span>
          <h3>{escape(skill_id)}</h3>
        </div>
        {bilingual_text(candidate["reason_ar"], candidate["reason_en"], "p", "domain-copy")}
        {bilingual_text(candidate["instead_ar"] if kind == "retire" else candidate["next_ar"], candidate["instead_en"] if kind == "retire" else candidate["next_en"], "p", "muted")}
      </article>
    """


def build_ui_skill_guide_payload():
    return {
        "artifact_paths": {
            "guide_markdown": str(UI_SKILLS_BOUNDARY_GUIDE_MD.relative_to(ROOT)),
            "contract_json": str(UI_SKILLS_BOUNDARY_CONTRACT_JSON.relative_to(ROOT)),
        },
        "summary": {
            "ar": "مرجع authoritative يثبت حدود منظومة UI skills: من ينسق، من ينفذ، من يقرأ المصدر، ومن يراجع الذوق أو النظام.",
            "en": "An authoritative guide that locks the boundaries of the UI skill stack: who orchestrates, who executes, who reads source truth, and who reviews taste or system behavior.",
        },
        "governance_overlay": UI_GOVERNANCE_OVERLAY,
        "comparison_contract": UI_COMPARISON_CONTRACT,
        "hud_contract": UI_HUD_CONTRACT,
        "sources": UI_GUIDE_OPENAI_DOC_LINKS,
    }


def build_ui_skill_guide_markdown(payload: dict) -> str:
    lines = [
        "# UI Skills Boundary Guide",
        "",
        "## Summary",
        f"- {payload['summary']['ar']}",
        f"- المخرج canonical: `{payload['artifact_paths']['guide_markdown']}`",
        f"- العقد الخام للآلة: `{payload['artifact_paths']['contract_json']}`",
        "- طبقة الحوكمة ليست peer داخل عنقود UI، بل overlay يُستدعى فقط عندما يغيّر الخطة أو الوثائق.",
        "",
        "## Taxonomy",
        "- Governance overlay: `god-plan-mode`, `plan-critic`, `openai-docs`",
        "- Orchestration: `omega_ui_product_brain`",
        "- Specialists: `figma_mcp_operator`, `product_flow_architect`, `ui_taste_critic`, `design_system_enforcer`, `premium_ui_generator`",
        "- Single-pass visual doctrine: `frontend-skill`",
        "",
        "## Governance Overlay",
    ]

    for item in payload["governance_overlay"]:
        lines.extend(
            [
                f"### `{item['skill_id']}`",
                f"- الدور: {item['job']['ar']}",
                f"- متى يدخل: {item['why']['ar']}",
                "",
            ]
        )

    lines.append("## Comparison Contract")
    lines.append("")
    for item in payload["comparison_contract"]:
        lines.extend(
            [
                f"### `{item['skill_id']}`",
                f"- الطبقة: {item['layer']['ar']}",
                f"- المهمة الأساسية: {item['primary_job']['ar']}",
                f"- أول اختيار عندما: {item['first_choice_when']['ar']}",
                f"- لا تستخدمه عندما: {item['do_not_use_when']['ar']}",
                f"- المدخلات: {'؛ '.join(value['ar'] for value in item['inputs'])}",
                f"- المخرجات: {'؛ '.join(value['ar'] for value in item['outputs'])}",
                f"- ما يجب حمايته: {', '.join(f'`{value}`' for value in item['protected_elements'])}",
                f"- يفشل إذا: {'؛ '.join(value['ar'] for value in item['failure_modes'])}",
                f"- handoff_to: {', '.join(f'`{value}`' for value in item['handoff_to'])}",
                f"- overlap_with: {', '.join(f'`{value}`' for value in item['overlap_with'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## HUD Contract",
            f"- Cluster summary: {payload['hud_contract']['cluster_summary']['ar']}",
            f"- Boundary note: {payload['hud_contract']['boundary_note']['ar']}",
            f"- Authority note: {payload['hud_contract']['authority_note']['ar']}",
            "",
            "### Handoff Order",
        ]
    )
    for index, step in enumerate(payload["hud_contract"]["handoff_order"], start=1):
        lines.append(
            f"{index}. {step['title']['ar']} — {step['detail']['ar']} | skills: {', '.join(f'`{value}`' for value in step['skills'])}"
        )

    lines.extend(["", "### Route Scenarios"])
    for route in payload["hud_contract"]["route_examples"]:
        lines.extend(
            [
                f"- `{route['scenario_id']}`: ابدأ بـ`{route['first_skill']}` | المسار الكامل: {', '.join(f'`{value}`' for value in route['path'])}",
                f"  {route['note']['ar']}",
            ]
        )

    lines.extend(["", "## Sources"])
    for source in payload["sources"]:
        lines.append(f"- {source['url']}")

    lines.append("")
    return "\n".join(lines)


def write_ui_skill_contract_artifacts(payload: dict):
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    UI_SKILLS_BOUNDARY_GUIDE_MD.write_text(build_ui_skill_guide_markdown(payload), encoding="utf-8")
    UI_SKILLS_BOUNDARY_CONTRACT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_shell(title_en: str, title_ar: str, page_class: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-default">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{escape(title_en)} | {escape(title_ar)}</title>
  <style>
    :root {{
      --bg: #03101d;
      --bg-soft: #071726;
      --panel: rgba(9, 21, 39, 0.82);
      --panel-strong: rgba(11, 25, 47, 0.92);
      --panel-soft: rgba(14, 30, 53, 0.72);
      --line: rgba(115, 196, 255, 0.22);
      --line-strong: rgba(0, 247, 230, 0.34);
      --ink: #edf8ff;
      --muted: rgba(237, 248, 255, 0.72);
      --dim: rgba(237, 248, 255, 0.52);
      --accent: #00f7e6;
      --accent-2: #4bc9ff;
      --warm: #f49b57;
      --danger: #ff7a78;
      --success: #7df2b9;
      --page-max: 1440px;
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 16px;
      --radius-sm: 12px;
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
      --body-font: "Segoe UI", "Tahoma", "DejaVu Sans", Arial, sans-serif;
      --mono-font: "DejaVu Sans Mono", "Cascadia Mono", "Liberation Mono", monospace;
    }}

    html[data-theme="light"] {{
      --bg: #edf4fb;
      --bg-soft: #f7fbff;
      --panel: rgba(255, 255, 255, 0.88);
      --panel-strong: rgba(255, 255, 255, 0.96);
      --panel-soft: rgba(239, 247, 255, 0.86);
      --line: rgba(24, 71, 112, 0.12);
      --line-strong: rgba(23, 104, 153, 0.22);
      --ink: #0e223a;
      --muted: rgba(14, 34, 58, 0.7);
      --dim: rgba(14, 34, 58, 0.55);
      --accent: #0c6f8a;
      --accent-2: #145e9c;
      --warm: #c9792e;
      --danger: #b8524c;
      --success: #197b55;
      --shadow: 0 24px 60px rgba(10, 35, 60, 0.12);
    }}

    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      min-height: 100%;
      background:
        radial-gradient(circle at 14% 14%, rgba(0, 247, 230, 0.12), transparent 28%),
        radial-gradient(circle at 84% 10%, rgba(75, 201, 255, 0.12), transparent 32%),
        radial-gradient(circle at 50% 100%, rgba(244, 155, 87, 0.10), transparent 34%),
        linear-gradient(180deg, var(--bg-soft) 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: var(--body-font);
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }}

    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(to right, rgba(0, 247, 230, 0.08) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 247, 230, 0.08) 1px, transparent 1px);
      background-size: 34px 34px;
      opacity: 0.18;
      mix-blend-mode: screen;
    }}

    body {{
      position: relative;
    }}

    a {{
      color: var(--accent-2);
    }}

    [data-ui-lang="ar"] [data-lang="en"],
    [data-ui-lang="en"] [data-lang="ar"] {{
      display: none !important;
    }}

    .page-shell {{
      width: min(100%, var(--page-max));
      margin: 0 auto;
      padding: 20px 18px 72px;
      display: grid;
      gap: 18px;
      position: relative;
      z-index: 1;
    }}

    .topbar {{
      position: sticky;
      top: 12px;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 14px 18px;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      background: var(--panel-strong);
      backdrop-filter: blur(14px);
      box-shadow: var(--shadow);
    }}

    .brand {{
      display: grid;
      gap: 4px;
    }}

    .brand strong {{
      font-size: 18px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .brand span {{
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.04em;
    }}

    .topbar__meta,
    .topbar__controls,
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}

    .chip,
    .state-chip,
    .score-badge,
    .tier-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(8, 20, 38, 0.22);
      color: var(--muted);
      font-size: 12px;
    }}

    html[data-theme="light"] .chip,
    html[data-theme="light"] .state-chip,
    html[data-theme="light"] .score-badge,
    html[data-theme="light"] .tier-badge {{
      background: rgba(255, 255, 255, 0.82);
    }}

    .chip-warning {{
      border-color: rgba(244, 155, 87, 0.36);
      color: var(--warm);
    }}

    .chip-muted {{
      color: var(--dim);
    }}

    .chip-code {{
      font-family: var(--mono-font);
      font-size: 11px;
      color: var(--ink);
    }}

    .hud-button {{
      cursor: pointer;
      border: 1px solid var(--line);
      background: rgba(6, 17, 32, 0.8);
      color: var(--ink);
      border-radius: 14px;
      padding: 10px 14px;
      font: inherit;
      min-height: 42px;
    }}

    html[data-theme="light"] .hud-button {{
      background: rgba(255, 255, 255, 0.86);
    }}

    .hero,
    .section-shell {{
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}

    .hero {{
      display: grid;
      gap: 18px;
      padding: 24px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0)),
        linear-gradient(180deg, rgba(9, 21, 39, 0.96), rgba(4, 12, 24, 0.98));
    }}

    html[data-theme="light"] .hero {{
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.44)),
        linear-gradient(180deg, rgba(239, 247, 255, 0.96), rgba(233, 241, 250, 0.98));
    }}

    .hero h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 1.08;
      max-width: 14ch;
    }}

    .accent {{
      color: var(--accent);
    }}

    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.8;
      max-width: 72ch;
    }}

    .hero-grid,
    .stats-grid,
    .domain-grid,
    .skills-grid,
    .exceptions-grid,
    .report-grid {{
      display: grid;
      gap: 14px;
    }}

    .hero-grid {{
      grid-template-columns: 1.4fr 1fr;
      align-items: stretch;
    }}

    .hero-card,
    .panel-card,
    .domain-card,
    .skill-card,
    .exception-card,
    .stat-card {{
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      background: var(--panel-soft);
      padding: 18px;
      display: grid;
      gap: 12px;
    }}

    .hero-card h2,
    .panel-card h2,
    .section-head h2,
    .domain-card h3,
    .stat-card h3,
    .exception-card h3 {{
      margin: 0;
    }}

    .section-shell {{
      padding: 20px;
      display: grid;
      gap: 16px;
    }}

    .section-head {{
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      justify-content: space-between;
      gap: 12px;
    }}

    .section-head p,
    .muted,
    .domain-copy,
    .skill-summary,
    .path-label {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
    }}

    .eyebrow {{
      margin: 0;
      color: var(--accent);
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}

    .stats-grid {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}

    .stat-card strong {{
      font-size: 28px;
      line-height: 1;
    }}

    .section-subtle {{
      color: var(--dim);
      font-size: 13px;
      line-height: 1.7;
    }}

    .domain-grid {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}

    .skills-grid {{
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }}

    .exceptions-grid,
    .report-grid {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}

    .skill-card__top,
    .domain-card__header,
    .meta-list,
    .report-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}

    .skill-card h3 {{
      margin: 0;
      font-size: 21px;
    }}

    .skill-card__score {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}

    .tier-badge {{
      color: var(--ink);
    }}

    .tier-s {{
      border-color: rgba(0, 247, 230, 0.32);
      background: rgba(0, 247, 230, 0.12);
    }}

    .tier-a {{
      border-color: rgba(75, 201, 255, 0.32);
      background: rgba(75, 201, 255, 0.12);
    }}

    .tier-b {{
      border-color: rgba(244, 155, 87, 0.32);
      background: rgba(244, 155, 87, 0.12);
    }}

    .tier-c {{
      border-color: rgba(255, 122, 120, 0.32);
      background: rgba(255, 122, 120, 0.12);
    }}

    .breakdown-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
    }}

    .mini-stat {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px;
      display: grid;
      gap: 6px;
      background: rgba(255, 255, 255, 0.03);
    }}

    .mini-stat span {{
      color: var(--dim);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .mini-stat strong {{
      font-size: 15px;
    }}

    .meta-list {{
      color: var(--dim);
      font-size: 12px;
    }}

    .meta-list div {{
      display: grid;
      gap: 4px;
    }}

    .meta-list strong {{
      color: var(--ink);
      font-weight: 600;
    }}

    .legend-line {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 13px;
    }}

    .report-stack {{
      display: grid;
      gap: 10px;
    }}

    .report-list {{
      margin: 0;
      padding-inline-start: 18px;
      color: var(--muted);
      line-height: 1.8;
    }}

    .report-list li {{
      margin-bottom: 4px;
    }}

    .code-block {{
      margin: 0;
      padding: 14px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(4, 14, 27, 0.72);
      font-family: var(--mono-font);
      font-size: 12px;
      line-height: 1.65;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: var(--ink);
    }}

    html[data-theme="light"] .code-block {{
      background: rgba(242, 248, 255, 0.92);
    }}

    .source-list {{
      display: grid;
      gap: 10px;
    }}

    .source-list a {{
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px 14px;
      background: rgba(7, 18, 33, 0.34);
      color: inherit;
    }}

    html[data-theme="light"] .source-list a {{
      background: rgba(255, 255, 255, 0.9);
    }}

    .source-list strong {{
      display: block;
      margin-bottom: 4px;
    }}

    .path-label {{
      font-family: var(--mono-font);
      font-size: 12px;
      overflow-wrap: anywhere;
    }}

    .footer-note {{
      text-align: center;
      color: var(--dim);
      font-size: 12px;
      padding-top: 6px;
    }}

    @media (max-width: 1080px) {{
      .hero-grid {{
        grid-template-columns: 1fr;
      }}

      .stats-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 760px) {{
      .page-shell {{
        padding-inline: 12px;
      }}

      .topbar {{
        top: 8px;
        padding: 12px;
      }}

      .hero,
      .section-shell {{
        padding: 16px;
      }}

      .stats-grid,
      .domain-grid,
      .skills-grid,
      .exceptions-grid,
      .report-grid {{
        grid-template-columns: 1fr;
      }}

      .breakdown-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
  </style>
</head>
<body class="{escape(page_class)}">
  <div class="page-shell">
    {body}
    <div class="footer-note">OMEGA HUD / interactive local artifact / no external assets</div>
  </div>
  <script>
    (function () {{
      const root = document.documentElement;
      const langState = document.getElementById('lang-state');
      const themeState = document.getElementById('theme-state');
      const langButton = document.getElementById('lang-toggle');
      const themeButton = document.getElementById('theme-toggle');
      const langKey = 'omega.ui.lang';
      const themeKey = 'omega.ui.theme';
      const langLabels = {{
        ar: {{ lang: 'AR / RTL', themeDark: 'داكن', themeLight: 'فاتح' }},
        en: {{ lang: 'EN / LTR', themeDark: 'Dark', themeLight: 'Light' }}
      }};

      function loadSetting(key, fallback) {{
        try {{
          return localStorage.getItem(key) || fallback;
        }} catch (error) {{
          return fallback;
        }}
      }}

      function saveSetting(key, value) {{
        try {{
          localStorage.setItem(key, value);
        }} catch (error) {{
          void error;
        }}
      }}

      function applyLanguage(lang) {{
        root.setAttribute('data-ui-lang', lang);
        root.lang = lang;
        root.dir = lang === 'ar' ? 'rtl' : 'ltr';
      }}

      function applyTheme(theme) {{
        root.setAttribute('data-theme', theme);
      }}

      function refreshStateLabels() {{
        const lang = root.getAttribute('data-ui-lang');
        const theme = root.getAttribute('data-theme');
        if (langState) {{
          langState.textContent = langLabels[lang].lang;
        }}
        if (themeState) {{
          themeState.textContent = theme === 'dark' ? langLabels[lang].themeDark : langLabels[lang].themeLight;
        }}
      }}

      const initialLang = loadSetting(langKey, 'ar');
      const initialTheme = loadSetting(themeKey, 'dark');
      applyLanguage(initialLang);
      applyTheme(initialTheme);
      refreshStateLabels();

      if (langButton) {{
        langButton.addEventListener('click', function () {{
          const next = root.getAttribute('data-ui-lang') === 'ar' ? 'en' : 'ar';
          applyLanguage(next);
          saveSetting(langKey, next);
          refreshStateLabels();
        }});
      }}

      if (themeButton) {{
        themeButton.addEventListener('click', function () {{
          const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
          applyTheme(next);
          saveSetting(themeKey, next);
          refreshStateLabels();
        }});
      }}
    }})();
  </script>
</body>
</html>
"""


def build_topbar(brand_title_ar: str, brand_title_en: str, subtitle_ar: str, subtitle_en: str, meta_chips: list[str]) -> str:
    meta = "".join(meta_chips)
    return f"""
      <header class="topbar">
        <div class="brand">
          <strong>OMEGA HUD</strong>
          <span>{bilingual_html(brand_title_ar, brand_title_en, 'span')}</span>
        </div>
        <div class="topbar__meta">
          {meta}
        </div>
        <div class="topbar__controls">
          <span class="state-chip" id="lang-state"></span>
          <button class="hud-button" id="lang-toggle">{bilingual_html("تبديل اللغة", "Switch Lang", "span")}</button>
          <span class="state-chip" id="theme-state"></span>
          <button class="hud-button" id="theme-toggle">{bilingual_html("تبديل الثيم", "Switch Theme", "span")}</button>
        </div>
      </header>
    """


def build_skills_page(skills):
    top_level = [skill for skill in skills if not skill["is_exception"]]
    exceptions = [skill for skill in skills if skill["is_exception"]]
    top_level.sort(key=lambda item: (-item["score"], item["skill_id"]))
    best = top_level[0]
    tier_groups = {"S": [], "A": [], "B": [], "C": []}
    for skill in top_level:
        tier_groups[skill["tier"]].append(skill)

    generated_at = pretty_timestamp(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    meta_chips = [
        f'<span class="chip">catalog 39</span>',
        f'<span class="chip">top-level 37</span>',
        f'<span class="chip">system exceptions 2</span>',
        f'<span class="chip">generated {escape(generated_at)}</span>',
    ]
    topbar = build_topbar(
        "لوحة ترتيب المهارات",
        "Skill Ranking HUD",
        "تقرير تشغيلي تفاعلي لترتيب ودمج وتحسين المهارات",
        "Interactive operational report for ranking, merging, and improving skills",
        meta_chips,
    )
    hero = f"""
      <section class="hero">
        <div class="hero-grid">
          <div>
            {bilingual_text("خريطة تشغيلية حية للمهارات بعد مزامنة السجل مع المصدر الأصلي.", "A live operational map of the skills after syncing the registry with the source of truth.", "p", "eyebrow")}
            <h1>{bilingual_html("أفضل مهارة حاليًا: <span class=\"accent\">God Plan Mode</span>", "Best Overall Right Now: <span class=\"accent\">God Plan Mode</span>", "span")}</h1>
            {bilingual_text("الترتيب هنا مبني على قيمة تشغيلية فعلية: execution value، uniqueness، trigger clarity، maintenance cost inverse، وguardrail discipline.", "This ranking uses an operational value matrix: execution value, uniqueness, trigger clarity, maintenance-cost inverse, and guardrail discipline.", "p")}
          </div>
          <article class="hero-card">
            <div class="chip-row">
              <span class="tier-badge tier-s">BEST OVERALL</span>
              {code_chip(best["skill_id"])}
              <span class="score-badge">{best["score"]}/100</span>
            </div>
            <h2>{escape(best["display_name"])}</h2>
            {bilingual_text("السبب: أعلى leverage عبر التخطيط المعقد، ضبط المهمة، ربط الاستراتيجية بالإثبات، وتقليل التخمين قبل التنفيذ.", "Why it wins: the highest leverage across complex planning, mission framing, strategy selection, and proof-aware execution.", "p")}
            {bilingual_text(best["summary"], best["summary"], "p", "muted")}
            <div class="breakdown-grid">
              <div class="mini-stat"><span>execution</span><strong>{best["components"]["execution"]}/40</strong></div>
              <div class="mini-stat"><span>uniqueness</span><strong>{best["components"]["uniqueness"]}/20</strong></div>
              <div class="mini-stat"><span>clarity</span><strong>{best["components"]["clarity"]}/15</strong></div>
              <div class="mini-stat"><span>maintenance</span><strong>{best["components"]["maintenance"]}/15</strong></div>
              <div class="mini-stat"><span>guardrails</span><strong>{best["components"]["evidence"]}/10</strong></div>
            </div>
          </article>
        </div>
      </section>
    """

    system_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("الاستثناءات النظامية خارج المقارنة", "System Exceptions Outside Comparative Ranking", "span")}</h2>
            {bilingual_text("المهارات دي موثقة لأن لها مصدر صالح داخل `.system`، لكنها ليست جزءًا من tier comparison العام.", "These skills remain documented because they have valid `.system` sources, but they are excluded from comparative tier scoring.", "p", "section-subtle")}
          </div>
          <div class="chip-row">
            <span class="chip chip-warning">{bilingual_html("تم حذف استثناء قديم مكسور: arabic-output-guard", "Removed stale broken exception: arabic-output-guard", "span")}</span>
          </div>
        </div>
        <div class="exceptions-grid">
          {"".join(render_exception_card(skill) for skill in exceptions)}
        </div>
      </section>
    """

    efficiency_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Efficiency Tiers", "Efficiency Tiers", "span")}</h2>
            {bilingual_text("كل مهارة top-level موجودة هنا ومعاها score breakdown وملخص سريع. معنى S هنا: أعلى قيمة تشغيلية عامة.", "Every top-level skill appears here with a score breakdown and a short summary. Here, S means the highest general operational value.", "p", "section-subtle")}
          </div>
          <div class="legend-line">
            <span class="chip">E = execution</span>
            <span class="chip">U = uniqueness</span>
            <span class="chip">C = clarity</span>
            <span class="chip">M = maintenance inverse</span>
            <span class="chip">G = guardrails</span>
          </div>
        </div>
        <div class="domain-grid">
          {"".join(
              f'''<section class="panel-card">
                <div class="domain-card__header">
                  <span class="tier-badge tier-{tier.lower()}">{tier}</span>
                  <h3>{bilingual_html({"S": "Tier S / الأعلى كفاءة", "A": "Tier A / قوي جدًا", "B": "Tier B / مفيد", "C": "Tier C / تخصصي أو منخفض التكرار"}[tier], {"S": "Tier S / Highest efficiency", "A": "Tier A / Strong", "B": "Tier B / Useful", "C": "Tier C / Specialist"}[tier], "span")}</h3>
                </div>
                <div class="skills-grid">{"".join(render_skill_card(skill) for skill in tier_groups[tier])}</div>
              </section>'''
              for tier in ("S", "A", "B", "C")
          )}
        </div>
      </section>
    """

    merge_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Merge Candidates", "Merge Candidates", "span")}</h2>
            {bilingual_text("المقصود هنا consolidation candidates، وليس مهارات يفضّل استدعاؤها معًا في نفس الطلب.", "These are consolidation candidates, not skills that should always be called together in a single request.", "p", "section-subtle")}
          </div>
        </div>
        <div class="domain-grid">
          {"".join(render_merge_group(group) for group in MERGE_GROUPS)}
        </div>
      </section>
    """

    retire_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Retire / Skip Candidates", "Retire / Skip Candidates", "span")}</h2>
            {bilingual_text("هذا القسم توصية استخدامية فقط. المقصود تقليل الحمل الذهني، لا حذف المهارات من المصدر.", "This section is advisory only. The goal is to reduce mental load, not to delete skills from the source set.", "p", "section-subtle")}
          </div>
        </div>
        <div class="domain-grid">
          {"".join(render_candidate(candidate, "retire") for candidate in RETIRE_CANDIDATES)}
        </div>
      </section>
    """

    improve_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Improve Next", "Improve Next", "span")}</h2>
            {bilingual_text("معنى S هنا: أعلى أولوية تحسين، وليس أعلى كفاءة حالية.", "Here, S means highest improvement priority, not highest current efficiency.", "p", "section-subtle")}
          </div>
        </div>
        <div class="domain-grid">
          {"".join(render_candidate(candidate, "improve") for candidate in IMPROVE_CANDIDATES)}
        </div>
      </section>
    """

    sources_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Registry Notes And Sources", "Registry Notes And Sources", "span")}</h2>
            {bilingual_text("تمت مراجعة مهارات OpenAI ذات الحساسية الزمنية على ضوء الوثائق الرسمية الحالية قبل تثبيت التوثيق المضاف.", "Time-sensitive OpenAI-related skills were reviewed against current official documentation before finalizing the added registry docs.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="stat-card">
            <h3>{bilingual_html("ما الذي تغيّر في السجل؟", "What changed in the registry?", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html("تمت إضافة 5 أوصاف ناقصة: frontend-skill, omega-ai-runtime, omega-format, omega-proof-gate, omega-repo-map", "Added 5 missing descriptions: frontend-skill, omega-ai-runtime, omega-format, omega-proof-gate, omega-repo-map", "span")}</li>
              <li>{bilingual_html("إجمالي السجل الحالي: 39 entry = 37 top-level + 2 system exceptions صالحة", "Current registry total: 39 entries = 37 top-level skills + 2 valid system exceptions", "span")}</li>
              <li>{bilingual_html("تم حذف الاستثناء القديم arabic-output-guard لأن المصدر الفعلي لم يعد موجودًا", "Removed the stale arabic-output-guard exception because its source no longer exists", "span")}</li>
            </ul>
          </article>
          <article class="stat-card">
            <h3>{bilingual_html("روابط OpenAI الرسمية التي تم التحقق منها", "Official OpenAI links reviewed", "span")}</h3>
            <div class="source-list">
              {"".join(f'<a href="{escape(link["url"])}"><strong>{escape(link["label"])}</strong><span class="path-label">{escape(link["url"])}</span></a>' for link in OPENAI_DOC_LINKS)}
            </div>
          </article>
        </div>
      </section>
    """

    body = topbar + hero + system_section + efficiency_section + merge_section + retire_section + improve_section + sources_section
    return build_shell("Omega Skills HUD", "لوحة مهارات أوميجا", "skills-page", body)


def build_memory_page(skills, memory_snapshot):
    inspect = memory_snapshot["inspect"]
    triage = memory_snapshot["triage"]
    suggest_entries = memory_snapshot["suggest_entries"]
    key_counts = memory_snapshot["key_counts"]
    self_learn = memory_snapshot["self_learn"]
    baseline = memory_snapshot["baseline"] or {}
    top_level_count = len([skill for skill in skills if not skill["is_exception"]])
    total_entries = len(skills)
    generated_at = pretty_timestamp(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    meta_chips = [
        f'<span class="chip">memory pending {triage["pending_total"]}</span>',
        f'<span class="chip">patterns {self_learn["memory_summary"]["durable_pattern_count"]}</span>',
        f'<span class="chip">self-learn events {self_learn["health"]["event_sequence"]}</span>',
        f'<span class="chip">generated {escape(generated_at)}</span>',
    ]
    topbar = build_topbar(
        "ذاكرة وتعلّم أوميجا",
        "Omega Memory + Learning",
        "تقرير حي عن persistent-memory و self-learn وحدودهم الحالية",
        "A live report on persistent-memory, self-learn, and their current boundaries",
        meta_chips,
    )
    latest_event = self_learn["latest_event"]
    latest_reversible = self_learn["latest_reversible_event"]
    delta_pending = triage["pending_total"] - baseline.get("pending_total", triage["pending_total"])
    key_count_list = "".join(
        f'<li><code>{escape(key)}</code>: {count}</li>' for key, count in key_counts.most_common()
    )
    backlog_sample = "".join(
        f'<li><code>{escape(entry["key"])}</code> → {escape(entry["value"])}</li>'
        for entry in suggest_entries[:8]
    )
    hero = f"""
      <section class="hero">
        <div class="hero-grid">
          <div>
            {bilingual_text("القراءة الحالية: الذاكرة سليمة، لكن backlog كله تقريبًا ephemeral؛ و self-learn ما زال مضبوطًا على read-focused boundaries.", "Current reading: memory is healthy, but the backlog is almost entirely ephemeral; self-learn remains tightly bounded around read-focused behavior.", "p", "eyebrow")}
            <h1>{bilingual_html("الذاكرة <span class=\"accent\">مستقرة</span>، والتعلّم <span class=\"accent\">منضبط</span>، لكن لا يوجد auto-promotion.", "Memory is <span class=\"accent\">stable</span>, learning is <span class=\"accent\">disciplined</span>, and there is still no auto-promotion.", "span")}</h1>
            {bilingual_text("التقرير ده مبني على مخرجات فعلية من doctor / inspect / triage / suggest / self-learn report، وليس على وصف عام.", "This report is grounded in actual outputs from doctor / inspect / triage / suggest / self-learn report, not generic narration.", "p")}
          </div>
          <div class="stats-grid">
            <article class="stat-card">
              <p class="eyebrow">doctor</p>
              <strong>OK</strong>
              {bilingual_text("حالة التخزين صحية", "Storage is healthy", "p", "muted")}
            </article>
            <article class="stat-card">
              <p class="eyebrow">pending</p>
              <strong>{triage["pending_total"]}</strong>
              {bilingual_text("كلها pending بعد refresh", "All still pending after refresh", "p", "muted")}
            </article>
            <article class="stat-card">
              <p class="eyebrow">promotable</p>
              <strong>{triage["promotable_total"]}</strong>
              {bilingual_text("لا يوجد مرشح durable صالح الآن", "No durable promotable candidate right now", "p", "muted")}
            </article>
            <article class="stat-card">
              <p class="eyebrow">self-learn</p>
              <strong>{self_learn["health"]["event_sequence"]}</strong>
              {bilingual_text("عدد الأحداث المسجلة", "Recorded events", "p", "muted")}
            </article>
          </div>
        </div>
      </section>
    """

    memory_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Persistent Memory", "Persistent Memory", "span")}</h2>
            {bilingual_text("الذاكرة durable حافظت على تفضيلات التعاون الأساسية، لكن queue الحالية ephemerals فقط ولذلك لم يتم أي promotion.", "Durable memory preserved the core collaboration preferences, but the current queue is entirely ephemeral, so no promotion was performed.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="panel-card">
            <h3>{bilingual_html("الملف الشخصي durable", "Durable collaboration profile", "span")}</h3>
            <ul class="report-list">
              <li><code>communication.language</code> → {escape(inspect["language"])}</li>
              <li><code>communication.tone</code> → {escape(inspect["tone"])}</li>
              <li><code>assistant.expected_role</code> → {escape(inspect["role"])}</li>
              <li><code>workflow.plan_preference</code> → {escape(inspect["plan"])}</li>
              <li><code>workflow.review_preference</code> → {escape(inspect["review"])}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("مشهد المشروع الحالي", "Current project overlay", "span")}</h3>
            <ul class="report-list">
              <li><code>project.id</code> → {escape(inspect["project_id"])}</li>
              <li><code>project.domain</code> → {escape(inspect["domain"])}</li>
              <li><code>project.aliases</code> → {escape(inspect["aliases"])}</li>
              <li><code>root</code> → {escape(inspect["root_path"])}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("نتيجة triage الحالية", "Current triage result", "span")}</h3>
            <ul class="report-list">
              <li><code>pending_total</code> → {triage["pending_total"]}</li>
              <li><code>ephemeral_total</code> → {triage["ephemeral_total"]}</li>
              <li><code>promotable_total</code> → {triage["promotable_total"]}</li>
              <li><code>conflict_count</code> → {triage["conflict_count"]}</li>
            </ul>
            {bilingual_text("القراءة الأساسية: لا يوجد أي durable candidate صالح للترقية الآن.", "Bottom line: there is no valid durable candidate to promote right now.", "p", "muted")}
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("توزيع الـ backlog", "Backlog distribution", "span")}</h3>
            <ul class="report-list">
              {key_count_list}
            </ul>
          </article>
        </div>
      </section>
    """

    self_learn_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Self Learn", "Self Learn", "span")}</h2>
            {bilingual_text("في هذه المهمة تم استخدام observe و report فقط، بدون apply أو rollback جديدين داخل المهارة نفسها.", "For this task, self-learn was used in observe/report mode only, with no new apply or rollback inside the skill itself.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="panel-card">
            <h3>{bilingual_html("صحة المهارة", "Skill health", "span")}</h3>
            <ul class="report-list">
              <li><code>skill_version</code> → {escape(self_learn["health"]["skill_version"])}</li>
              <li><code>event_sequence</code> → {self_learn["health"]["event_sequence"]}</li>
              <li><code>successful_evolutions</code> → {self_learn["health"]["successful_evolutions"]}</li>
              <li><code>failed_evolutions</code> → {self_learn["health"]["failed_evolutions"]}</li>
              <li><code>last_verification_status</code> → {escape(self_learn["health"]["last_verification_status"])}</li>
              <li><code>current_renderer_profile</code> → {escape(self_learn["health"]["current_renderer_profile"])}</li>
              <li><code>active_patterns_count</code> → {self_learn["health"]["active_patterns_count"]}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("آخر حدث", "Latest event", "span")}</h3>
            <pre class="code-block">{escape(json.dumps(latest_event, ensure_ascii=False, indent=2))}</pre>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("آخر حدث reversible", "Latest reversible event", "span")}</h3>
            <pre class="code-block">{escape(json.dumps(latest_reversible, ensure_ascii=False, indent=2))}</pre>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("الذاكرة الداخلية الحالية", "Current internal memory state", "span")}</h3>
            <ul class="report-list">
              <li><code>journal_event_count</code> → {self_learn["memory_summary"]["journal_event_count"]}</li>
              <li><code>durable_pattern_count</code> → {self_learn["memory_summary"]["durable_pattern_count"]}</li>
              <li><code>suppressed_fingerprint_count</code> → {self_learn["memory_summary"]["suppressed_fingerprint_count"]}</li>
              <li><code>apply_mode</code> → {escape(self_learn["decision_cache"]["recent_trusted_defaults"]["apply_mode"])}</li>
              <li><code>prefer_propose_for_freeform</code> → {escape(str(self_learn["decision_cache"]["recent_trusted_defaults"]["prefer_propose_for_freeform"]).lower())}</li>
            </ul>
          </article>
        </div>
      </section>
    """

    changes_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("What Changed", "What Changed", "span")}</h2>
            {bilingual_text("القسم ده يفرق بين ما تم تحديثه فعليًا، وما تمت ملاحظته فقط، وما بقي خارج النطاق.", "This section separates what was truly updated, what was only observed, and what stayed out of scope.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="panel-card">
            <h3>{bilingual_html("تحديث السجل", "Registry refresh", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html("تمت إضافة 5 أوصاف ناقصة للسجل", "Added 5 missing description files to the registry", "span")}</li>
              <li>{bilingual_html(f"إجمالي السجل الآن {total_entries} entry منها {top_level_count} top-level", f"Registry now tracks {total_entries} entries, including {top_level_count} top-level skills", "span")}</li>
              <li>{bilingual_html("تم حذف الاستثناء المكسور arabic-output-guard لأن المصدر غير موجود", "Removed the broken arabic-output-guard exception because the source is missing", "span")}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("تحديث الذاكرة", "Memory refresh", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html(f"الـ pending الحالي = {triage['pending_total']} (التغير مقابل آخر baseline محفوظ: {delta_pending:+d})", f"Current pending count = {triage['pending_total']} (delta vs previous saved baseline: {delta_pending:+d})", "span")}</li>
              <li>{bilingual_html("لم يتم أي promote أو forget أو rollback على ذاكرة المشروع", "No promote, forget, or rollback action was applied to project memory", "span")}</li>
              <li>{bilingual_html("سبب عدم الترقية: كل العناصر المتبقية ephemerals وغير promotable في policy الحالية", "Why no promotion: every remaining item is ephemeral and non-promotable under the current policy", "span")}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("تحديث self-learn", "Self-learn refresh", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html(f"event_sequence وصل إلى {self_learn['health']['event_sequence']} بعد observe جديد فقط", f"event_sequence reached {self_learn['health']['event_sequence']} after a new observe-only event", "span")}</li>
              <li>{bilingual_html("لم يتم استخدام apply في هذه المهمة احترامًا لحدود self-only", "No apply was used in this task to respect the self-only boundary", "span")}</li>
              <li>{bilingual_html("آخر verification status ما زال rolled-back من تاريخ سابق، ولم تتم إعادة كتابة هذا السجل", "The last verification status remains rolled-back from a prior event, and this refresh did not rewrite that history", "span")}</li>
            </ul>
          </article>
        </div>
      </section>
    """

    boundaries_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Boundaries", "Boundaries", "span")}</h2>
            {bilingual_text("الحدود هنا جزء من الجودة، لا قيد سلبي. هي اللي بتخلّي القراءة صادقة وما تخليش التقرير يدّعي قدرات غير موجودة.", "The boundaries are part of the quality bar, not a negative limitation. They keep the report honest and prevent fake capability claims.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="panel-card">
            <h3>{bilingual_html("لماذا self-learn لم يحدّث باقي المهارات؟", "Why self-learn did not update other skills", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html("عقد self-learn الحالي self-only ومحلي داخل مجلده فقط", "The current self-learn contract is self-only and local to its own skill directory", "span")}</li>
              <li>{bilingual_html("هذه المهمة استخدمت observe/report كأدلة تشغيلية فقط", "This task used observe/report as operational evidence only", "span")}</li>
              <li>{bilingual_html("تحديث باقي السجل تم يدويًا داخل مساحة العمل لأن هذا هو النطاق الصحيح هنا", "The rest of the registry was updated manually inside the workspace because that is the correct scope here", "span")}</li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("لماذا persistent-memory لم يروّج backlog تلقائيًا؟", "Why persistent-memory did not auto-promote the backlog", "span")}</h3>
            <ul class="report-list">
              <li>{bilingual_html("سياسة الذاكرة تمنع auto-promotion أصلًا", "The memory policy forbids auto-promotion in the first place", "span")}</li>
              <li>{bilingual_html("المتبقي كله مفاتيح ephemeral مثل project.active_artifact و project.root_fact", "The remaining queue is entirely ephemeral keys such as project.active_artifact and project.root_fact", "span")}</li>
              <li>{bilingual_html("حتى بعد backfill، لا يوجد durable candidate صالح وخالٍ من المخاطر يستحق promotion", "Even after backfill, there is still no safe durable candidate worth promoting", "span")}</li>
            </ul>
          </article>
        </div>
      </section>
    """

    evidence_section = f"""
      <section class="section-shell">
        <div class="section-head">
          <div>
            <h2>{bilingual_html("Evidence Ledger", "Evidence Ledger", "span")}</h2>
            {bilingual_text("مصادر هذه القراءة كلها محلية ومباشرة، مع مراجعة رسمية إضافية لوثائق OpenAI للمهارات ذات الحساسية الزمنية.", "Every source below is local and direct, with an extra official review pass for time-sensitive OpenAI-oriented skills.", "p", "section-subtle")}
          </div>
        </div>
        <div class="report-grid">
          <article class="panel-card">
            <h3>{bilingual_html("الأوامر المستخدمة", "Commands used", "span")}</h3>
            <pre class="code-block">python3 "$PMEM" inspect --cwd "$PWD" --format markdown
python3 "$PMEM" triage --cwd "$PWD" --format markdown
python3 "$PMEM" suggest --cwd "$PWD"
python3 "$PMEM" doctor
python3 "$SELF_LEARN" --intent report --json</pre>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("عينات من الـ backlog", "Backlog sample", "span")}</h3>
            <ul class="report-list">
              {backlog_sample}
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("ملفات مرجعية", "Reference files", "span")}</h3>
            <ul class="report-list">
              <li><code>omega-runtime/skills/OMEGA_SKILL_CATALOG.yaml</code></li>
              <li><code>output/reports/persistent-memory-status-report.md</code></li>
              <li><code>~/.codex/skills/self-learn/SKILL.md</code></li>
              <li><code>~/.codex/skills/persistent-memory/SKILL.md</code></li>
            </ul>
          </article>
          <article class="panel-card">
            <h3>{bilingual_html("روابط OpenAI الرسمية المراجَعة", "Official OpenAI links reviewed", "span")}</h3>
            <div class="source-list">
              {"".join(f'<a href="{escape(link["url"])}"><strong>{escape(link["label"])}</strong><span class="path-label">{escape(link["url"])}</span></a>' for link in OPENAI_DOC_LINKS)}
            </div>
          </article>
        </div>
      </section>
    """

    body = topbar + hero + memory_section + self_learn_section + changes_section + boundaries_section + evidence_section
    return build_shell("Omega Memory Learning Report", "تقرير ذاكرة وتعلّم أوميجا", "memory-page", body)


def main():
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    skills = build_skill_index()
    memory_snapshot = build_memory_snapshot()
    write_ui_skill_contract_artifacts(build_ui_skill_guide_payload())
    (OUTPUT_HTML_DIR / "omega-skills-hud.html").write_text(build_skills_page(skills), encoding="utf-8")
    (OUTPUT_HTML_DIR / "omega-memory-learning-report.html").write_text(build_memory_page(skills, memory_snapshot), encoding="utf-8")
    print("Wrote:")
    print(OUTPUT_HTML_DIR / "omega-skills-hud.html")
    print(OUTPUT_HTML_DIR / "omega-memory-learning-report.html")
    print(UI_SKILLS_BOUNDARY_GUIDE_MD)
    print(UI_SKILLS_BOUNDARY_CONTRACT_JSON)


if __name__ == "__main__":
    main()
